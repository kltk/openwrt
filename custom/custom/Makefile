include $(TOPDIR)/rules.mk

PKG_NAME:=helloworld
PKG_RELEASE:=1
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
	SECTION:=utils
	CATEGORY:=Utilities
	TITLE:=Helloworld -- prints a snarky message
  KCONFIG:=\
    CONFIG_KEXEC=y \
    CONFIG_KEXEC_FILE=y \
    CONFIG_NF_CONNTRACK_DSCPREMARK_EXT=y
endef

define Package/$(PKG_NAME)/description
	It's my first package demo.
endef

# define Package/$(PKG_NAME)/config
#   TITLE:=Custom
#   KCONFIG:=\
#     CONFIG_KEXEC=y \
#     CONFIG_KEXEC_FILE=y \
#     CONFIG_NF_CONNTRACK_DSCPREMARK_EXT=y
# endef

define Build/Prepare
	echo "Here is Package/Prepare"
	# mkdir -p $(PKG_BUILD_DIR)
  #   $(CP) ./src/* $(PKG_BUILD_DIR)/
endef

define Package/$(PKG_NAME)/install
	echo "Here is Package/install"
	# $(INSTALL_DIR) $(1)/bin
	# $(INSTALL_BIN) $(PKG_BUILD_DIR)/$(PKG_NAME) $(1)/bin/
endef
	
$(eval $(call BuildPackage,$(PKG_NAME)))