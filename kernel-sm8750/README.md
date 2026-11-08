# kernel-sm8750 RPM template

This is a source-build template for the Xiaomi Pad 8 Pro SM8750 kernel. It
uses the exact local configuration:

```text
piano-kernel-7.2.15-sm8750-gd2710cd.config
```

The resulting kernel release is:

```text
7.2.15-sm8750-gd2710cd
```

The `piano-boot.dtb` beside the spec comes from the project release package:

```text
xiaomipad-8pro-mainline
  linux-image-7.2.15-piano58_7.2.15-58.1_arm64.deb
  /usr/lib/linux-image-7.2.15-piano58/piano-boot.dtb
```

It is the already composed project DTB, not a raw `make dtbs` output and not a
DTB taken from the `piano-debian` workspace. The exact source and hash are
recorded in `piano-boot.dtb.provenance.json`. Replace it only with a DTB
audited against the same kernel and board inputs.

## Required source files

Copy or download these into `$HOME/rpmbuild/SOURCES`:

```text
linux-sm8750-piano-d2710cd13b337ef5172bd2394839e9d9673ff88a.tar.gz
piano-kernel-7.2.15-sm8750-gd2710cd.config
piano-boot.dtb
v4l2loopback-0.15.4.tar.gz
```

The source commit is pinned in `kernel-sm8750.spec`. Do not substitute a
different kernel tree without changing the config and DTB inputs together.

## Build

```sh
mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS,tmp}
install -m0644 piano-kernel-7.2.15-sm8750-gd2710cd.config ~/rpmbuild/SOURCES/
install -m0644 piano-boot.dtb ~/rpmbuild/SOURCES/
spectool -g -R kernel-sm8750.spec
TMPDIR=$HOME/rpmbuild/tmp rpmbuild -ba --nodebuginfo \
  --define '_topdir %{getenv:HOME}/rpmbuild' kernel-sm8750.spec
```

`spectool` needs network access. If the source tarballs are already present,
skip that command.

## Kernel package behavior

The RPM installs:

```text
/boot/Image-7.2.15-sm8750-gd2710cd
/boot/vmlinuz-7.2.15-sm8750-gd2710cd
/boot/System.map-7.2.15-sm8750-gd2710cd
/boot/config-7.2.15-sm8750-gd2710cd
/usr/lib/modules/7.2.15-sm8750-gd2710cd/
/usr/lib/linux-image/7.2.15-sm8750-gd2710cd/piano-boot.dtb
/usr/lib/linux-image/7.2.15-sm8750-gd2710cd/qcom/*.dtb
```

It also includes the matching external module:

```text
/usr/lib/modules/7.2.15-sm8750-gd2710cd/extra/v4l2loopback.ko
```

and declares:

```spec
Provides: piano-camera-loopback
Provides: kmod(v4l2loopback)
```

On a real system, `%posttrans` runs `dracut` and then the installed
`/etc/kernel/postinst.d/zz-piano-boot` hook. That hook calls
`/usr/sbin/piano-boot-update`, which is the qbootctl-based local updater.
The chroot/installroot case skips both operations.

The package does not contain a store-based `piano-boot-switch` system.
