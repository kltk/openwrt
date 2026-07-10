#!/bin/bash

sed -i ':a;N;$!ba s/\\\n\s[+]luci-app-attendedsysupgrade//' feeds/luci/collections/luci-ssl/Makefile
sed -i ':a;N;$!ba s/\\\n\s[+]luci-app-attendedsysupgrade//' feeds/luci/collections/luci-ssl-openssl/Makefile
sed -i ':a;N;$!ba s/\\\n\s[+]luci-app-attendedsysupgrade//' feeds/luci/collections/luci-nginx/Makefile
sed -i ':a;N;$!ba s/\\\n\s[+]luci-app-attendedsysupgrade//' feeds/luci/collections/luci/Makefile
