#
# Copyright (C) 2022 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=ath11k-firmware
PKG_SOURCE_DATE:=2022-12-14
PKG_SOURCE_VERSION:=ab1229f94591ec4ffb16410e359b7f618be75a33
PKG_MIRROR_HASH:=48a2526971e56a3be1c80b72cd82b9932c196b4ab9b7d5dc35117f0548a8fe57
PKG_RELEASE:=1

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/kvalo/ath11k-firmware.git

PKG_LICENSE_FILES:=LICENSE.qca_firmware

PKG_MAINTAINER:=Robert Marko <robimarko@gmail.com>

include $(INCLUDE_DIR)/package.mk

RSTRIP:=:
STRIP:=:

define Package/ath11k-firmware-default
  SECTION:=firmware
  CATEGORY:=Firmware
  URL:=$(PKG_SOURCE_URL)
  DEPENDS:=
endef

define Package/ath11k-firmware-ipq6018
$(Package/ath11k-firmware-default)
  TITLE:=ath11k firmware for IPQ6018 devices
endef

define Package/ath11k-firmware-ipq8074
$(Package/ath11k-firmware-default)
  TITLE:=ath11k firmware for IPQ8074 devices
endef

define Package/ath11k-firmware-qcn9074
$(Package/ath11k-firmware-default)
  TITLE:=ath11k firmware for QCN9074 devices
endef

define Build/Compile

endef

define Package/ath11k-firmware-ipq6018/install
	$(INSTALL_DIR) $(1)/lib/firmware/IPQ6018
	$(INSTALL_DATA) \
		$(PKG_BUILD_DIR)/IPQ6018/hw1.0/2.4.0.1/WLAN.HK.2.4.0.1-01746-QCAHKSWPL_SILICONZ-1/* \
		$(1)/lib/firmware/IPQ6018/
endef
QCN9074_BOARD_REV:=8e140c65f36137714b6d8934e09dcd73cb05c2f6
QCN9074_BOARD_FILE:=board-2.bin.$(QCN9074_BOARD_REV)

define Download/qcn9074-board
  URL:=https://github.com/kvalo/ath11k-firmware/raw/master/QCN9074/hw1.0/
  URL_FILE:=board-2.bin
  FILE:=$(QCN9074_BOARD_FILE)
  HASH:=dbf0ca14aa1229eccd48f26f1026901b9718b143bd30b51b8ea67c84ba6207f1
endef
$(eval $(call Download,qcn9074-board))

define Package/ath11k-firmware-ipq8074/install
	$(INSTALL_DIR) $(1)/lib/firmware/IPQ8074
	$(INSTALL_DIR) $(1)/lib/firmware/ath11k/IPQ8074/hw2.0
	$(INSTALL_DATA) \
		$(PKG_BUILD_DIR)/ath11k-firmware/IPQ8074/hw2.0/testing/2.9.0.1/WLAN.HK.2.9.0.1-01385-QCAHKSWPL_SILICONZ-1/* \
		$(1)/lib/firmware/IPQ8074/
	$(INSTALL_BIN) \
		$(PKG_BUILD_DIR)/IPQ8074/hw2.0/board-2.bin $(1)/lib/firmware/ath11k/IPQ8074/hw2.0/board-2.bin
endef

define Package/ath11k-firmware-qcn9074/install
	$(INSTALL_DIR) $(1)/lib/firmware/ath11k/QCN9074/hw1.0
	$(INSTALL_DATA) \
		$(PKG_BUILD_DIR)/ath11k-firmware/QCN9074/hw1.0/testing/2.9.0.1/WLAN.HK.2.9.0.1-01385-QCAHKSWPL_SILICONZ-1/* \
		$(1)/lib/firmware/ath11k/QCN9074/hw1.0/
	$(INSTALL_BIN) \
		$(DL_DIR)/$(QCN9074_BOARD_FILE) $(1)/lib/firmware/ath11k/QCN9074/hw1.0/board-2.bin
endef

$(eval $(call BuildPackage,ath11k-firmware-ipq6018))
$(eval $(call BuildPackage,ath11k-firmware-ipq8074))
$(eval $(call BuildPackage,ath11k-firmware-qcn9074))
