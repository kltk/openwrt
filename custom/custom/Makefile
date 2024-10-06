PKG_NAME:=custom
PKG_RELEASE:=1
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)

define KernelPackage/$(PKG_NAME)
	SECTION:=utils
	CATEGORY:=Utilities
	TITLE:=Custom -- prints a snarky message
	KCONFIG:=\
		CONFIG_KEXEC=y \
		CONFIG_KEXEC_FILE=y \
		CONFIG_NF_CONNTRACK_DSCPREMARK_EXT=y
endef

define KernelPackage/$(PKG_NAME)/description
	It's my first package demo.
endef

$(eval $(call KernelPackage,$(PKG_NAME)))
