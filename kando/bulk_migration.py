#!/usr/bin/env python3
"""
Simple one-time script to migrate specific directories from 
/iplant/home/shared/commons_repo/ to CKAN.

Usage: python3 migrate_commons.py <username> <password>
"""

import sys
import de
import utils.migrate as migrate_utils

BASE_PATH = "/iplant/home/shared/commons_repo/curated"

# List of all directories to migrate
DIRECTORIES = [
    "Alcock_leafPhenotypingImages_2016",
    "alexsaunders_BangladeshFloodData_2024",
    "Bacher_Wheat_DroughtStress_Dec2016",
    "Beissinger_MaizeTeo_2016",
    "Benes_SegmentedProceduralSorghumPlants_2022",
    "Bertioli_Arachis_genome_supplement_TVDM_Mar2019",
    "Bsail_cotton_plant_part_segmentation_3d_lidar_2022",
    "Bucksch_Cassava-Supplemental-Material-Plants-Peope-Planet_6-9-2020",
    "Bucksch_DIRT3D-Models-PlantPhysiology_Jun2021",
    "Bucksch_Liu_ThePlantPhenomeJournal_2023",
    "Bunting_DI_CPS_Mini_Tests_Mar2022",
    "Bunting_Vehicle_Test_01_April2022",
    "Bunting_Vehicle_Test_02_April2022",
    "Bunting_Vehicle_Test_03_April2022",
    "Bunting_Vehicle_Test_04_April2022",
    "Bunting_Vehicle_Test_05_April2022",
    "Bunting_Vehicle_Test_06_April2022",
    "Carolyn_Lawrence_Dill_G2F_Mar_2017",
    "Carolyn_Lawrence_Dill_G2F_Nov_2016_V.3",
    "Carolyn_Lawrence_Dill_GOMAP_Banana_NCBI_ASM31385v2_December_2022_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Banana_NCBI_ASM31385v2_February_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Barley_IBSC_PGSB-1.0_May_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Barley_IPK_cv_Morex_V3_June_2023_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_BarrelClover_A17_HM341_Mt4.0v2_August_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Barrel_Clover_LIS_A17.gnm5.ann1_6.L2RX_November_2022_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Barrel_Clover_LIS_R108.gnmHiC_1.ann1.Y8NH_November_2022_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_BarrelClover_R108_HM340_v1.0_August_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Bdistachyon.Bd21.v3.1_November_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Blueberry_GigaDB_Draper_v1.0_May_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Blueberry_GigaDB_v1.0_June_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Cacao_NCBI_CriolloV2_December_2022_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Cacao_NCBI_CriolloV2_March_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Cannabis_NCBI_cs10_2.0_October_2022_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Cannabis_NCBI-cs10_January_2020.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Canola_BnPIR_ZS11_March_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Coffee_CGH_v1.0_June_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Coffee_CGH_v1.0_May_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_CommonBean_DOE-JGI-USDA-NIFA.2.0_August_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_CommonBean_LIS_G19833_November_2022_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Cotton_DOE-JGI_v2.1_June_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Cowpea_JGI_IT97K-499-35_December_2022_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Cowpea_JGI.v1.1_August_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Gossypium_raimondii_JGI_v2.1_January_2020.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Grape_Genoscope_12x_January_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Grape_Genoscope_12x_May_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Hop_HopBase_Cascade_January_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Hop_HopBase_Cascade_July_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_CyVerse_Mo17_CAU_2.0_July_2023.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_B73_NAM_5.0_December_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_B73_NAM_5.0_October_2022_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_B97_NAM_1.0_October_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML103_NAM_1.0_October_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML228_NAM_1.0_October_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML247_NAM_1.0_October_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML277_NAM_1.0_October_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML322_NAM_1.0_October_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML333_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML52_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_CML69_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_HP301_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Il14H_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Ki11_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Ki3_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Ky21_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_M162W_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_M37W_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Mo17_CAU_1.0_May_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Mo18W_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Ms71_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_NC350_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_NC358_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Oh43_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Oh7B_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_P39_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_PH207_NS-UIUC_UMN_1.0_May_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Tx303_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_Tzi8_NAM_1.0_November_2022.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Maize_MaizeGDB_W22_NRGENE_2.0_May_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_maize.Mo17.AGPv1_April_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_maize.PH207.UIUC_UMN-1.0_April_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_maize.W22.AGPv2_April_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Peanut_Tifrunner.IPGI.1.0_August_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Peanut_Tifrunner.IPGI.2.0_November_2022_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Pepper_PGP_CM334_November_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Pepper_PGP_cvCM334_June_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Rapeseed_BnPIR_ZS11_June_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Rice_IRGSP-1.0_April_2019.r2",
    "Carolyn_Lawrence_Dill_GOMAP_Rice_IRGSP-1.0_February_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Rice_IRGSP_1.0_June_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Sbicolor.BTx623.v3.0.1_November_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Solanum_lycopersicum_ITAG4.1.v1_April_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Solanum_pennellii_Bolger2014.v1_April_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Sorghum_DOE-JGI_v3.1.1_March_2023_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Soybean_JGI-Wm82.a4.v1_April_2019.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Soybean_LIS_Wm82_IGA1008.gnm1.ann1.FGN6_May_2023_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Stiff_brome_DOE-JGI_Bd21_v3.2_May_2023_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_SugarPine_TreeGenesDB-1.5_January_2020.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Sugar_Pine_TreeGenes_v1.5_June_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Tea_Teabase_CSS_ChrLev_20200506_June_2023_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Tea_TPIA_CSS_ChrLev_20200506_September_2021.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Tomato_SGN_SL4.0_July_2023_v2.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Wheat_RefSeq1.1_HC_December_2018.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Wheat_URGI_IWGSC_RefSeq_v2.1_May_2023_v1.r1",
    "Carolyn_Lawrence_Dill_GOMAP_Wild_Tomato_SGN_LA716_June_2023_v2.r1",
    "Carolyn_Lawrence_Dill_maize-GAMER_July_2017_V.1",
    "Carolyn_Lawrence-Dill_maize-GAMER_maize.B73_RefGen_v4_Zm00001d.2_Oct_2017.r1",
    "Carolyn_Lawrence_Dill_Maize_WiDiv_Association_Studies_Dataset_September_2023",
    "Carolyn_Lawrence_Dill_Maize_WiDiv_Summer_2021_Dataset_June_2023",
    "Carvalho_Schnable_C4grasses-UNL_NICGH-2018",
    "ChenyongMiao_MaizeLeafCountImages_2019",
    "Cimen_Jensen_TrnaThermometer_Sep2020",
    "CondonMaxwell_ScienceAdvances_2019",
    "Cook_KernelArchitecturePlantPhys_Feb2012",
    "Copetti_Kyuss_assembly_annotation_March_2021",
    "Copetti_Norin61_Fhb1_2020",
    "Copetti_Rabiosa_annotation_Feb2021",
    "CourtneyGiebink_UTincre_May2021",
    "CS19_G2F",
    "Daniel_Laspisa_B73_RefGen_v4CEN_Feb_2019",
    "DeanVik_MArVD2_Apr2022",
    "DeGraaf_data_comparison_lateral_groundwater_flows_2022",
    "deGraaf_hyper-resolution_parameterizition",
    "Demieville_sorghumDataNote_2025",
    "*deprecated*Carolyn_Lawrence_Dill_G2F_Nov_2016_V1",
    "*deprecated*Carolyn_Lawrence_Dill_G2F_Nov_2016_V2",
    "*deprecated*Ramstein_SNPConstraintPrediction_2021",
    "dos_Santos_Genomic_Prediction_2019",
    "Duitama_rice_variation_2015",
    "E01MalariaClinical_plasmodb_March2019",
    "E02MalariaClinical_plasmodb_March2019",
    "E03MalariaClinical-plasmodb_Sept2018",
    "E04MalariaClinical-plasmodb_Sept2018",
    "E13MalariaClinical-plasmodb_Sept2018",
    "E15MalariaCore-plasmodb_Jan2019",
    "E20MalariaClinical_plasmodb_March2019",
    "E21MalariaClinical_plasmodb_March2019",
    "E23MalariaClinical-plasmodb_Sept2018",
    "E24MalariaClinical-plasmodb_Sept2018",
    "E25MalariaClinical-plasmodb_Sept2018",
    "E30MalariaClinical-plasmodb_March2019",
    "Edgar_Spalding_G2F_Inbred_Ear_Imaging_June_2017",
    "Edward_Buckler_Tassel_5_Dec_2016",
    "Edwards_DesiGenome_Jun2016",
    "Edwards_KabuliGenome_Jun2016",
    "EHTC_2017L1_May2022",
    "EHTC_2018L1_Dec2024",
    "EHTC_CenA2017_Jul2021",
    "EHTC_First3C279Results_May2020",
    "EHTC_FirstM87Results_Apr2019",
    "EHTC_FirstSgrAPol_Mar2024",
    "EHTC_FirstSgrAResults_May2022",
    "EHTC_M87-2018_Mar2024",
    "EHTC_M87mwl2017_Apr2021",
    "EHTC_M87mwl2018_Dec2024",
    "EHTC_M87pol2017_Nov2023",
    "EHTC_metadata2018_Dec2023",
    "EHTC_MonitoringM87_Sep2020",
    "EHTC_SgrAmwl2017_May2022",
    "Enders_Hirsch_maizeSeedlingColdStress_2018",
    "erodene_supplemental_field_data_2019",
    "EvansDeyHeilman_PinusEdulis_ringwidth_2024",
    "FIA_PIPO_AZ_TREE_RING_DEC2021",
    "G2F_Planting_Season_2015_v2",
    "Gage_LatentSpacePhenotyping_2019",
    "Gage_tassel_selection_2018",
    "Gage_uORF_allelic_variation_2021",
    "Gault_tripsacumTranscriptomes_Aug2018",
    "GazituaVik_ETSPviruses_Oct2019",
    "GenomesToFields_2014_2017_v1",
    "GenomesToFields_data_2019",
    "GenomesToFields_G2F_2016_Data_Mar_2018",
    "GenomesToFields_G2F_Data_2018",
    "GenomesToFields_G2F_data_2020",
    "GenomesToFields_G2F_data_2021",
    "GenomesToFields_G2F_data_2022",
    "GenomesToFields_G2F_data_2023",
    "GenomesToFields_G2F_genotypic_data_2014_to_2023",
    "GenomesToFields_G2F_Indigo_Microbiome_Data_2017-2018",
    "GenomesToFields_GenotypeByEnvironment_PredictionCompetition_2023",
    "GenomesToFields_GenotypeByEnvironment_PredictionCompetition_2025",
    "Giezendanner_BangladeshCNNLSTMModelData_June2023",
    "Giezendanner_BangladeshInundationHistory_Mai2023",
    "Gillan_Ecosphere_2021",
    "Gillan_et_al_RAMA_2019",
    "HaixiaoHu_OatMultOmicsPred_Jun2021",
    "HaixiaoHu_PBJOatTranscriptome_Oct2019",
    "Howard-Varona_and_Vik_et_al_Phage_therapy_2018",
    "Hurwitz_imicrobe_mock_communities_2018",
    "IOMAP_Genomes_Data_2017",
    "Jaiswal_chia_atlas_2017",
    "Jensen_plantProteomeProfiling_Jun2021",
    "Jensen_proteinTemp_Jun2021",
    "Jensen_sorghumPHG_Sep2019",
    "JHUAPL_plantCT_2020",
    "JianmingYu_Sorghum_Jun2019",
    "Jinliang_Yang_pvp_diallel_data_2017",
    "JZhang_LCondon_CONUS_Topography_Sep2020",
    "Kalbfleisch_EquCab3_2018",
    "kandemirRuiAndersonWang_stomata_microtubules_analysis_Aug2019",
    "Kremling_maizeDiversityPanelRNAseq_2018",
    "Kremling_Nature3RNASeq282_March2018",
    "LaurenThatch_SJBM_Feb2021",
    "Lent_SCKE_Nov2017",
    "Liang_Schnable_UNLPlantVision_2017",
    "Lin_CuticularWaxGWASTWAS_2024",
    "Liu_Wang_maize_syn10_2015",
    "LiWang_GERPload_Nov2017",
    "LMATL_SmartphoneHealthAndActivity_2020",
    "MaizeCode_annotation_evidence_data_2017",
    "MartinezMeyer_et_al_DivDist_2021",
    "McConnell_ZeroCoverageRegions_2022",
    "Meyer_ATML1_fluctuations_2016",
    "Miao_Schnable_sorghumHighThroughputPhenotyping_2017",
    "mosaic_raamp2",
    "Murray_G2F_UAV_Maize_2018",
    "Nelson_Brassicaceae_lincRNAs_Mar2022",
    "oneKP_capstone_2019",
    "Pope_Impact_of_Green_Infrastructure_on_Canopy_Height_2017",
    "Qi_Sun_Zea_mays_haplotype_map_2018",
    "QiuyueChen_Teosinte_Maize_SNP_May2020",
    "RahulBhadani_scAGN_Apr2022",
    "Ramstein_AmesNAMHybrids_2019",
    "Ramstein_SNPConstraintPrediction_2022",
    "Reicher_PooledProteinTagging_2020",
    "Rodriguez_MaizePhenolics_2022",
    "Rohit_GlobalSurfaceWaterDataset_2024",
    "Rohit_UrbanFloodObservation_2024",
    "Saengwilai_cassavaRootphenotypes_2019",
    "Sandia_RUBRIC_2018",
    "Sang_LowPhosphate_Algae_Study_Feb2018",
    "Schneider_CentromereDeletionMaps_2015",
    "Shenton_OofficinalisAnnotation_2019",
    "Sixiang_Wen_Xray_spectrum_slim_disk_table_model_2022",
    "Spinti_river_fragmentation_data_2022",
    "Springer_maize_B73_epigenetics_2017",
    "Springer_maize_CML322__epigenetics_2017",
    "Springer_maize_Mo17_epigenetics_2017",
    "Springer_maize_Oh43_epigenetics_2017",
    "Springer_maize_Tx303_epigenetics_2017",
    "Stapleton_MaizeLeafMicrobesByLeafAge_2015",
    "Steyaert_ResOpsUS_April_2021",
    "Sumitani_singleCellData_2022",
    "Tadych_AzGroundwaterSpatialAnalysis_Aug2023",
    "tamu_corn_2017_CS17_G2F_20190305",
    "TerraByte_PlantLabImages_2021",
    "Thomas_seedlingRootPhenotypingImages_2016",
    "Tirado_HyperspecSaltStressExp_2019",
    "Topp_Zea_mays_2d_DIRT_2016",
    "Topp_Zea_mays_gel_3d_2016",
    "Topp_Zea_mays_xray_volumes_2016",
    "Tran_UpperCO_simulation_Sep2020",
    "Triplett_heihehydrology_Apr22",
    "UF_resende_Sweet_corn_2020",
    "Valluru2019Genetics",
    "Varabyou_RNAseqNoise_2020",
    "Vertnet_Amphibia_July2018",
    "VertNet_Amphibia_Oct2015",
    "Vertnet_Amphibia_Sep2016",
    "Vertnet_Aves_July2018",
    "VertNet_Aves_Oct2015",
    "Vertnet_Aves_Sep2016",
    "Vertnet_Fishes_July2018",
    "VertNet_Fishes_Oct2015",
    "Vertnet_Fishes_Sep2016",
    "Vertnet_Mammalia_July2018",
    "VertNet_Mammalia_Oct2015",
    "Vertnet_Mammalia_Sep2016",
    "Vertnet_Reptilia_July2018",
    "VertNet_Reptilia_Oct2015",
    "Vertnet_Reptilia_Sep2016",
    "VertNet_Traits",
    "Volpato_etal_2020_DPM_Soybeans",
    "Zayed_efam_2020.1",
    "ZayedWainainaDominguez-Huerta_RNAevolution_Dec2021",
    "Zayed_Xfam_2020.1",
    "Zhijie_FloodPlanet_2023",
    "Zhong_Barrow_2019",
    "Zhong_Barrow_Viromes_2018",
    "Zhou_Jander_MaizeLeafMetabolomeGWAS_2019"
]

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 migrate_commons.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print(f"Starting migration of {len(DIRECTORIES)} directories...")
    
    # Authenticate
    print("Authenticating...")
    token = de.get_de_api_key(username, password)
    if token is None:
        print("ERROR: Authentication failed.")
        sys.exit(1)
    
    print("Authentication successful.")
    
    # Migrate each directory
    success = 0
    failed = []
    
    for i, dir_name in enumerate(DIRECTORIES, 1):
        full_path = f"{BASE_PATH}/{dir_name}"
        
        print(f"[{i:3d}/{len(DIRECTORIES)}] {full_path}...", end=' ')
        
        try:
            result = migrate_utils.migrate_dataset_to_ckan(
                username, password, full_path, dir_name, 
                f"Dataset migrated from {full_path}", "Unknown"
            )
            
            if "successfully" in result.lower():
                print("✓")
                success += 1
            else:
                print(f"✗ ({result})")
                failed.append((dir_name, result))
        except Exception as e:
            print(f"✗ ({str(e)})")
            failed.append((dir_name, str(e)))
    
    # Summary
    print(f"\nMigration complete!")
    print(f"Successful: {success}")
    print(f"Failed: {len(failed)}")
    print(f"Total: {len(DIRECTORIES)}")
    
    if failed:
        print(f"\nFailed directories:")
        for name, error in failed[:10]:  # Show first 10 failures
            print(f"  {name}: {error[:100]}...")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")

if __name__ == "__main__":
    main()