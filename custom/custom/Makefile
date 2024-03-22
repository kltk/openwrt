include $(TOPDIR)/rules.mk

PKG_NAME:=custom

define Package/$(PKG_NAME)/config
  TITLE:=Custom
  KCONFIG:=\
    CONFIG_KEXEC=y \
    CONFIG_KEXEC_FILE=y \
    CONFIG_NF_CONNTRACK_DSCPREMARK_EXT=y
endef

include $(TOPDIR)/feeds/luci/luci.mk
