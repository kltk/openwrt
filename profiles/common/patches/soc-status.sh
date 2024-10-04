#!/bin/bash
pwd
ls -al
ls -al feeds
ls -al feeds/luci
cd feeds/luci
git apply -p0 --ignore-space-change --ignore-whitespace <<'EOF'
diff --git a/modules/luci-base/root/sbin/soc-status b/modules/luci-base/root/sbin/soc-status
new file mode 100755
--- /dev/null
+++ b/modules/luci-base/root/sbin/soc-status
@@ -0,0 +1,64 @@
+#!/bin/sh
+# shellcheck disable=SC2155
+
+get_cpu_freq() {
+  local value="$(cat /sys/devices/system/cpu/cpufreq/policy0/scaling_cur_freq 2>/dev/null)"
+  [ -n "$value" ] || value="0"
+  echo "$value"
+}
+
+get_cpu_governor() {
+  local value="$(cat /sys/devices/system/cpu/cpufreq/policy0/scaling_governor 2>/dev/null)"
+  [ -n "$value" ] || value="unknown"
+  echo "$value"
+}
+
+get_cpu_temp() {
+  local value="$(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | sort -n | tail -1)"
+  [ -n "$value" ] || value="-1"
+  echo "$value"
+}
+
+get_wifi_temp() {
+  local value="$(cat /sys/class/ieee80211/phy*/hwmon*/temp*_input 2>/dev/null | sort -n | tail -1)"
+  [ -n "$value" ] || value="-1"
+  echo "$value"
+}
+
+get_cpu_usage() {
+  local value="$(top -b -n1 | awk '/^CPU/ { print 100-$8 }')"
+  [ -n "$value" ] || value="-1"
+  echo "$value"
+}
+
+get_nss_usage() {
+  local value="$(grep '%' /sys/kernel/debug/qca-nss-drv/stats/cpu_load_ubi 2>/dev/null | awk '{print $2}' | sed 's/%//')"
+  [ -n "$value" ] || value="-1"
+  echo "$value"
+}
+
+case "$1" in
+  cpu_freq)
+    get_cpu_freq
+    ;;
+  cpu_governor)
+    get_cpu_governor
+    ;;
+  cpu_temp)
+    get_cpu_temp | awk '{ printf("%.1f\n", $1/1000) }'
+    ;;
+  wifi_temp)
+    get_wifi_temp | awk '{ printf("%.1f\n", $1/1000) }'
+    ;;
+  cpu_usage)
+    get_cpu_usage
+    ;;
+  nss_usage)
+    get_nss_usage
+    ;;
+  *)
+    echo "Usage: $0 {cpu_freq|cpu_governor|cpu_temp|wifi_temp|cpu_usage|nss_usage}"
+    exit 1
+    ;;
+esac
EOF
git apply -p0 --ignore-space-change --ignore-whitespace <<'EOF'
diff --git a/modules/luci-base/root/usr/share/rpcd/ucode/luci b/modules/luci-base/root/usr/share/rpcd/ucode/luci
--- modules/luci-base/root/usr/share/rpcd/ucode/luci
+++ modules/luci-base/root/usr/share/rpcd/ucode/luci
@@ -581,8 +581,59 @@
 			return { result: ports };
 		}
 	},
 
+	getCoreInfo: {
+		call: function() {
+			let fd;
+			let result = {};
+
+			fd = popen('soc-status cpu_freq');
+			result.cpufreq = trim(fd.read('all'));
+			fd.close();
+
+			fd = popen('soc-status cpu_governor');
+			result.governor = trim(fd.read('all'));
+			fd.close();
+
+			return result;
+		}
+	},
+
+	getCoreTemp: {
+		call: function() {
+			let fd;
+			let result = {};
+
+			fd = popen('soc-status cpu_temp');
+			result.cpu = trim(fd.read('all'));
+			fd.close();
+
+			fd = popen('soc-status wifi_temp');
+			result.wifi = trim(fd.read('all'));
+			fd.close();
+
+			return result;
+		}
+	},
+
+	getCoreUsage: {
+		call: function() {
+			let fd;
+			let result = {};
+
+			fd = popen('soc-status cpu_usage');
+			result.cpu = trim(fd.read('all'));
+			fd.close();
+
+			fd = popen('soc-status nss_usage');
+			result.nss = trim(fd.read('all'));
+			fd.close();
+
+			return result;
+		}
+	},
+
 	getCPUBench: {
 		call: function() {
 			return { cpubench: readfile('/etc/bench.log') || '' };
 		}
EOF
git apply -p0 --ignore-space-change --ignore-whitespace <<'EOF'
diff --git a/modules/luci-mod-status/htdocs/luci-static/resources/view/status/include/10_system.js b/modules/luci-mod-status/htdocs/luci-static/resources/view/status/include/10_system.js
--- modules/luci-mod-status/htdocs/luci-static/resources/view/status/include/10_system.js
+++ modules/luci-mod-status/htdocs/luci-static/resources/view/status/include/10_system.js
@@ -7,8 +7,23 @@
 	object: 'luci',
 	method: 'getVersion'
 });
 
+var callCoreInfo = rpc.declare({
+	object: 'luci',
+	method: 'getCoreInfo'
+});
+
+var callCoreTemp = rpc.declare({
+	object: 'luci',
+	method: 'getCoreTemp'
+});
+
+var callCoreUsage = rpc.declare({
+	object: 'luci',
+	method: 'getCoreUsage'
+});
+
 var callSystemBoard = rpc.declare({
 	object: 'system',
 	method: 'board'
 });
@@ -48,9 +63,12 @@
 			L.resolveDefault(callCPUBench(), {}),
 			L.resolveDefault(callCPUInfo(), {}),
 			L.resolveDefault(callCPUUsage(), {}),
 			L.resolveDefault(callTempInfo(), {}),
-			L.resolveDefault(callLuciVersion(), { revision: _('unknown version'), branch: 'LuCI' })
+			L.resolveDefault(callLuciVersion(), { revision: _('unknown version'), branch: 'LuCI' }),
+			L.resolveDefault(callCoreInfo(), {}),
+			L.resolveDefault(callCoreTemp(), {}),
+			L.resolveDefault(callCoreUsage(), {})
 		]);
 	},
 
 	render: function(data) {
@@ -59,9 +77,12 @@
 		    cpubench    = data[2],
 		    cpuinfo     = data[3],
 		    cpuusage    = data[4],
 		    tempinfo    = data[5],
-		    luciversion = data[6];
+		    luciversion = data[6],
+		    coreinfo    = data[7],
+		    coretemp    = data[8],
+		    coreusage   = data[9];
 
 		luciversion = luciversion.branch + ' ' + luciversion.revision;
 
 		var datestr = null;
@@ -92,9 +113,12 @@
 				systeminfo.load[0] / 65535.0,
 				systeminfo.load[1] / 65535.0,
 				systeminfo.load[2] / 65535.0
 			) : null,
-			_('CPU usage (%)'),    cpuusage.cpuusage
+			_('CPU usage (%)'),    cpuusage.cpuusage,
+			_('核心频率'),          coreinfo.cpufreq / 1000 + ' MHz ' + '(' + coreinfo.governor + ')',
+			_('核心温度'),          'CPU ' + coretemp.cpu + ' °C' + ' / ' + 'WiFi ' + coretemp.wifi + ' °C',
+			_('使用率'),            'CPU ' + coreusage.cpu + '%' + ' / ' + 'NSS ' + coreusage.nss + '%'
 		];
 
 		if (tempinfo.tempinfo) {
 			fields.splice(6, 0, _('Temperature'));
EOF
git apply -p0 --ignore-space-change --ignore-whitespace <<'EOF'
diff --git a/modules/luci-mod-status/root/usr/share/rpcd/acl.d/luci-mod-status.json b/modules/luci-mod-status/root/usr/share/rpcd/acl.d/luci-mod-status.json
--- modules/luci-mod-status/root/usr/share/rpcd/acl.d/luci-mod-status.json
+++ modules/luci-mod-status/root/usr/share/rpcd/acl.d/luci-mod-status.json
@@ -2,9 +2,9 @@
 	"luci-mod-status-realtime": {
 		"description": "Grant access to realtime statistics",
 		"read": {
 			"ubus": {
-				"luci": [ "getConntrackList", "getRealtimeStats", "getCPUBench", "getCPUUsage", "getOnlineUsers" ],
+				"luci": [ "getConntrackList", "getRealtimeStats", "getCPUBench", "getCPUUsage", "getOnlineUsers", "getCoreInfo", "getCoreTemp", "getCoreUsage" ],
 				"network.rrdns": [ "lookup" ]
 			}
 		}
 	},
EOF