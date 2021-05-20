#!/usr/bin/env python3
import logging
logger = logging.getLogger(__name__)
import json
import subprocess
import requests
import warnings
import cern_sso
import pickle
import os.path

def getAODSIMName(dasName):
    if dasName.endswith("/AODSIM") or dasName.endswith("/GEN-SIM"):
        return dasName
    elif dasName.endswith("AODSIM"): ## nano->mini or mini->aod
        try:
            parent_resp = subprocess.check_output(["dasgoclient", "-json", "-query", f"parent dataset={dasName}"])
            parentName = json.loads(parent_resp)[0]["parent"][0]["parent_dataset"]
            logger.debug(f"    {dasName} --> {parentName}")
        except Exception as ex:
            logger.error(f"Problem getting parent dataset for {dasName}")
            return
        return getAODSIMName(parentName)
    else:
        raise ValueError("Cannot find ancestor AODSIM for dataset of tier {0}".format(dasName.split("/")[-1]))

def getMcMPrepID(aodSimName):
    prepid_resp = subprocess.check_output(["dasgoclient", "-json", "-query", f"dataset dataset={aodSimName} | grep dataset.prepid"])
    return next(itm for itm in json.loads(prepid_resp) if "dbs3:dataset_info" in itm["das"]["services"])["dataset"][0]["prep_id"]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find the McM prep IDs and generator settings for a MiniAOD or NanoAOD sample")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("dataset", nargs="+", help="Dataset names in DAS (MINI/NANO/)AODSIM")
    parser.add_argument("--cernSSOcookies", type=str, help="Pickled cookie jar with CERN SSO cookies for https://cms-pdmv.cern.ch/mcm/ (to cache between subsequent runs - remove if expired)" )
    args = parser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.verbose else logging.INFO))

    prodcookies = None
    if args.cernSSOcookies:
        if os.path.isfile(args.cernSSOcookies):
            with open(args.cernSSOcookies, "rb") as f:
                prodcookies = pickle.load(f)
    if not prodcookies:
        import cern_sso
        prodcookies = cern_sso.krb_sign_on("https://cms-pdmv.cern.ch/mcm/", verify=False)                     
        if args.cernSSOcookies:
            with open(args.cernSSOcookies, "wb") as f:
                pickle.dump(prodcookies, f)

    from pprint import pprint
    from collections import defaultdict
    for dataset in args.dataset:
        aodSim = getAODSIMName(dataset)
        aodsimPrepID = getMcMPrepID(aodSim)
        logger.debug(f"prep_id for {aodSim}: {aodsimPrepID}")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            req_aod = requests.get(f"https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get/{aodsimPrepID}", verify=False).json()["results"]
            chainId = req_aod["member_of_chain"][0]
            logger.debug(f"Chained prep ID: {chainId}")
            req_chain = requests.get(f"https://cms-pdmv.cern.ch/mcm/restapi/chained_requests/get/{chainId}", verify=False, cookies=prodcookies).json()["results"]
            #pprint(req_chain["chain"])
            lhePrepID = next(cReq for cReq in req_chain["chain"] if "wmLHE" in cReq)
            req_lhe = requests.get(f"https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get/{lhePrepID}", verify=False).json()["results"]
            print(f"# {req_chain['dataset_name']}")
            if req_lhe["notes"]:
                #print("-----  NOTES   -----")
                print(req_lhe["notes"])
                #print("-----   END    -----")
            else:
                print("----- FRAGMENT -----")
                print(req_lhe["fragment"])
                print("-----   END    -----")
            gridpack = next(ln for ln in req_lhe["fragment"].split("\n") if "/gridpacks/" in ln).split("vstring")[1].strip("(),").strip("'\"")
            print(f"Gridpack: {gridpack}")
            gen_p = max(req_lhe["generator_parameters"], key=lambda entry : entry["version"]) 
            print(f"Cross-section {gen_p['cross_section']:f}pb, filter efficiency {gen_p['filter_efficiency']:f} +/- {gen_p['filter_efficiency_error']:f}, match efficiency {gen_p['match_efficiency']:f} +/- {gen_p['match_efficiency_error']:f}, negative weights fraction {gen_p.get('negative_weights_fraction', 0.):f} (v{gen_p['version']:d}, {gen_p['submission_details']['author_name']} {gen_p['submission_details']['submission_date']})")
            gsPrepID = None
            if "GS" not in lhePrepID:
                gsPrepID = next(cReq for cReq in req_chain["chain"] if "GS" in cReq)
                req_gensim = requests.get(f"https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get/{gsPrepID}", verify=False).json()["results"]
                if not req_gensim["fragment"]:
                    print(f"Fragment name: {req_gensim['name_of_fragment']}")
