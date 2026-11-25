%global debug_package %{nil}
%global __strip /bin/true
%global _firmwaredir %{_prefix}/lib/firmware
%global upstream_tag v1.6.3
%global audioreach_commit 2af1f1ebb8d4fd03b5f53891467ddde2e208a8a0

Name:           xiaomi-piano-firmware
Version:        0.7+os3.0.303.0
Release:        3%{?dist}
Summary:        Firmware for Xiaomi Pad 8 Pro (piano)
License:        LicenseRef-Proprietary-Firmware AND BSD-3-Clause
URL:            https://github.com/yzddmr6/xiaomipad-8pro-mainline
BuildArch:      noarch
Source0:        piano-firmware-%{upstream_tag}.tar.gz
Source1:        https://github.com/linux-msm/audioreach-topology/archive/%{audioreach_commit}.tar.gz#/audioreach-topology-2af1f1eb.tar.gz
# alsatplg lives in alsa-topology-utils, not in alsa-utils.
BuildRequires:  alsa-topology-utils
BuildRequires:  m4
BuildRequires:  python3
Provides:       piano-local-firmware = %{version}-%{release}
Obsoletes:      piano-local-firmware <= %{version}-%{release}

%description
Firmware and static hardware configuration for the Xiaomi Pad 8 Pro
(SM8750, piano). The blobs are the ones pinned by the OS3.0.303.0.WPYCNXM
locks in firmware/piano-*.json; the two ALSA topologies are compiled here
from device/audio against the audioreach-topology commit recorded in
device/audio/source.json.

%prep
%autosetup -n piano-firmware
# The topology macros include the upstream audioreach graphs.
mkdir audioreach
tar -xzf %{SOURCE1} -C audioreach --strip-components=1

%build
m4 -I audioreach device/audio/Piano-Capture-Diag.m4 > Piano-Capture-Diag.conf
alsatplg -c Piano-Capture-Diag.conf -o Piano-Capture-Diag-tplg.bin
m4 -I device/audio -I audioreach device/audio/Xiaomi-Pad-8-Pro.m4 > Xiaomi-Pad-8-Pro.conf
alsatplg -c Xiaomi-Pad-8-Pro.conf -o Xiaomi-Pad-8-Pro-tplg.bin
# The kernel loads these exact bytes; refuse a toolchain that changes them.
python3 - <<'PY'
import hashlib, json, pathlib, sys
for lock, built in (('diagnostic.json', 'Piano-Capture-Diag-tplg.bin'),
                    ('card.json', 'Xiaomi-Pad-8-Pro-tplg.bin')):
    topology = json.loads(pathlib.Path('device/audio', lock).read_text())['topology']
    data = pathlib.Path(built).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != topology['bytes'] or digest != topology['sha256']:
        sys.exit(f'{built}: {len(data)} bytes {digest}, '
                 f"expected {topology['bytes']} {topology['sha256']}")
PY

%install
python3 - <<'PY'
import json, pathlib, sys
sys.path.insert(0, 'tools')
import firmware_payload
rows = firmware_payload.load_tree()
firmware_payload.stage_tree(rows, 'firmware', '%{buildroot}%{_firmwaredir}')
locks = sorted(pathlib.Path('firmware').glob('piano-*.json'))
builds = {json.loads(p.read_text()).get('stock_build') for p in locks} - {None}
if len(builds) != 1:
    sys.exit('the firmware locks must name one stock build')
topologies = [json.loads(pathlib.Path('device/audio', name).read_text())['topology']
              for name in ('diagnostic.json', 'card.json')]
doc = pathlib.Path('%{buildroot}%{_datadir}/doc/%{name}')
doc.mkdir(parents=True)
(doc / 'inputs.json').write_text(json.dumps({
    'stock_build': builds.pop(), 'files': rows,
    'topologies': [{k: t[k] for k in ('path', 'bytes', 'sha256')} for t in topologies],
}, indent=2) + '\n')
PY
install -Dm644 Piano-Capture-Diag-tplg.bin \
    %{buildroot}%{_firmwaredir}/qcom/sm8750/Piano-Capture-Diag-tplg.bin
install -Dm644 Xiaomi-Pad-8-Pro-tplg.bin \
    %{buildroot}%{_firmwaredir}/qcom/sm8750/Xiaomi-Pad-8-Pro-tplg.bin

%files
%license LICENSES/LicenseRef-Proprietary-Firmware.txt LICENSES/audioreach-BSD-3-Clause.txt
%doc %{_datadir}/doc/%{name}/inputs.json
%{_firmwaredir}/ath12k
%{_firmwaredir}/foursemi
%{_firmwaredir}/nanosic
%{_firmwaredir}/novatek
%{_firmwaredir}/qca
%{_firmwaredir}/qcom

%changelog
* Wed Nov 25 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.7+os3.0.303.0-3
- Build from the upstream source tree instead of converting the Ubuntu deb:
  stage the locked blobs with firmware_payload and compile both ALSA topologies
  with m4 and alsatplg against the pinned audioreach commit
- Fail the build when a toolchain changes the topology bytes the kernel loads
- Describe the payload in inputs.json and ship the licences directly

* Sat Nov 21 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.7+os3.0.303.0-2
- Disable brp-strip so the ath12k board file keeps the checksum locked by the deb

* Fri Nov 13 2026 GhfunNiHe <131235947+GhfunNiHe@users.noreply.github.com> - 0.7+os3.0.303.0-1
- Include the CDSP compute images and their split segments

* Mon Nov 09 2026 Piano RPM template <noreply@localhost> - 0.6+os3.0.303.0-1
- Convert piano-local-firmware to xiaomi-piano-firmware
