define Device/linksys_mr7350
       $(call Device/FitImage)
       $(call Device/UbiFit)
       DEVICE_VENDOR := Linksys
       DEVICE_MODEL := MR7350
       BLOCKSIZE := 128k
       PAGESIZE := 2048
       SOC := ipq6018
       DEVICE_PACKAGES := ipq-wifi-linksys_mr7350
endef
TARGET_DEVICES += linksys_mr7350

define Device/netgear_wax214
       $(call Device/FitImage)
       $(call Device/UbiFit)
       DEVICE_VENDOR := Netgear
       DEVICE_MODEL := WAX214
       BLOCKSIZE := 128k
       PAGESIZE := 2048
       DEVICE_DTS_CONFIG := config@cp03-c1
       SOC := ipq6018
       DEVICE_PACKAGES := ipq-wifi-netgear_wax214
endef
TARGET_DEVICES += netgear_wax214