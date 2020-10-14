#SELECT  '("'+ new_destination_path + '", "' + old_destination_path + '"),', * FROM [UberFactory].[dbo].[ub_new_customers]
#WHERE new_customer_id in (10941,10942,10943,10944,10945,10946,10947,10948,10949,10950,10951,10952,10953,10954,10955,10956,10957,10958,10959,10960,10961,10962,10963,10964,10965,10966,10967,10968)


feeds_FredericConstant = [("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmgermany/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORADMGermany_c87a15b1-42ed-4ad0-9210-0172ffc99882/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmfrance/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORADMFrance_b28aed7b-5440-4bfd-965e-c2f6f96e804c/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmswitzerland/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORADMSwitzerland_d358c4c0-d64a-42d0-85ea-734d53d676bd/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmusa/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORADMUSA_d2f3b8a9-9a4b-4de8-a2e2-ea6e7c2c814b/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinafrance/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORAlpinaFrance_ead97c31-c193-4e76-8e6c-533ad08a6dbc/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinagermany/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORAlpinaGermany_c7036dcb-3ae8-4c0d-8f3b-443dc15add45/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinaswitzerland/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORAlpinaSwitzerland_26ce0a87-eed5-4669-9884-66ac5699973a/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinausa/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORAlpinaUSA_025d86c5-59b2-4eb5-adaa-f630e541e41a/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcfrance/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORFCFrance_8df839a4-b9ac-4ce0-8c3e-27f9cf054af7/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcgermany/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORFCGermany_6bfca785-2645-43e1-81db-519b97fa7137/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcswitzerland/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORFCSwitzerland_36aa4c61-ee3b-472f-b537-c52766afde23/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcusa/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORFCUSA_51970da9-4fcb-4775-a46a-991f4e44815a/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmspain/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorSpain_860c5488-61c8-4897-ad8e-78ff50a8ad2b/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmitaly/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorADMItaly_734cafb7-0469-4edf-8fd8-6c2552202605/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmportugal/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorADMPortugal_d888e4e8-8f0b-4ab2-b1b6-564b196774ed/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmnetherlands/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorADMNetherlands_8556c470-8df9-4ed8-a34f-f3cbecd3cb75/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAdmuk/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_ADMMonitorUK_0d63ff87-5c10-43a1-a85f-fb40834584f2/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinaspain/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorAlpinaSpain_3a9f3d87-e88b-4538-88da-baf36886c557/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinaitaly/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorAlpinaItaly_b22ecda1-2df1-4d96-8d31-2d053806ad64/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinaportugal/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorAlpinaPortugal_5156af6e-99c5-4a88-835b-2902dc97b060/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinanetherlands/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorAlpinaNetherlands_af34f41e-7c13-4a0c-904b-51392e8a8ae1/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantAlpinauk/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_AlpinaMONITORUK_26122d55-1ad6-4abc-a5f3-1861cb62739b/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcspain/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorFCSpain_ca8c54fd-b780-4bb8-b38d-13bdea82746a/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcportugal/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORFCPortugal_6153eac6-dbf3-4a41-bae8-41e69c7587c3/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcitaly/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorFCItaly_e0b49739-28de-40cd-b1ab-83376807624a/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcnetherlands/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORFCNetherlands_d79ddc05-3c02-4c59-8cd5-ec5702bb9244/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcuk/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MonitorUK_f0ea9f89-daf7-4fa6-8ea3-6fcdd8077019/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_FrederiqueConstant_FrederiqueconstantFcdenmark/feed.xml", "https://data.hosting.augure.com/factory/Augure_FC_FrederiqueConstant_MONITORFCDenmark_6254217a-4124-4222-99be-b5273cde1e32/feed.xml")]

feeds_Bucherer = [("https://data.hosting.augure.com/uberfactory/Ubermetrics_France_CarlfbuchererBuchererswitzerland/feed.xml", "https://data.hosting.augure.com/factory/Augure_Bucherer_CARLFBUCHERER_MONITORBuchererSwitzerland_57331285-a47d-4c73-b588-c2f704b61fd4/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_France_CarlfbuchererBucherergermany/feed.xml", "https://data.hosting.augure.com/factory/Augure_Bucherer_CARLFBUCHERER_MONITORBuchererGermany_8ad5ea9d-aca0-4012-850d-f9a77e3a3904/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_France_CarlfbuchererBuchereraustria/feed.xml", "https://data.hosting.augure.com/factory/Augure_Bucherer_CARLFBUCHERER_MONITORBuchererAustria_d16d44e2-f10e-4a78-b5ed-ff6ac1bb808c/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_France_CarlfbuchererBuchererfrance/feed.xml", "https://data.hosting.augure.com/factory/Augure_Bucherer_CARLFBUCHERER_MONITORBuchererFrance_aeb28eba-dc41-4ded-a3ef-347863ea6b90/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_France_CarlfbuchererBuchererdenmark/feed.xml", "https://data.hosting.augure.com/factory/Augure_Bucherer_CARLFBUCHERER_MONITORBuchererDenmark_81503554-4cad-4dab-8885-c6770a350c9d/feed.xml"),
("https://data.hosting.augure.com/uberfactory/Ubermetrics_France_CarlfbuchererBuchereruk/feed.xml", "https://data.hosting.augure.com/factory/Augure_Bucherer_CARLFBUCHERER_MONITORBuchererUK_62be7de2-f558-411a-a1ad-a939e349befb/feed.xml")]

def generate_queries(feeds):
    print('BEGIN TRAN')
    print("")
    tmp_select = ""

    for feed in feeds:
        new_feed = feed[0]
        old_feed = feed[1]
        
        print("INSERT INTO ContratPige (CodeContrat, CodeSociete, FournisseurPige, LibelleContrat, [Automatic], _c_CLIENT_FEED, _c_SEGMENT_DESTINATION, _c_CLIENT_FEED_TYPE, _c_DUREE_TENTATIVES_RECUPERATION, _c_FTP_PORT, _c_UPDATEMEDIA)")
        print("SELECT CodeContrat+10000, CodeSociete, FournisseurPige, LibelleContrat, [Automatic],'" + new_feed + "', _c_SEGMENT_DESTINATION, _c_CLIENT_FEED_TYPE, _c_DUREE_TENTATIVES_RECUPERATION, _c_FTP_PORT, _c_UPDATEMEDIA")
        print("FROM ContratPige")
        print("WHERE _c_CLIENT_FEED='" + old_feed + "'")
        
        print ("UPDATE ContratPige SET Automatic = 'N' WHERE _c_CLIENT_FEED='" + old_feed + "'")
        print("")

        if len(tmp_select) > 0:
            tmp_select += " OR "
        
        tmp_select += "(_c_CLIENT_FEED='" + old_feed + "' OR _c_CLIENT_FEED='" + new_feed + "')"
    
    print ("SELECT * FROM ContratPige WHERE " + tmp_select + " ORDER BY CodeSociete")
    print ('ROLLBACK TRAN')

#generate_queries(feeds_FredericConstant)
generate_queries(feeds_Bucherer)
