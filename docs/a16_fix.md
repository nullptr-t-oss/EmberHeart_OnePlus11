# Fix Slow Boot when using NetHunter on Android 16+ (Restorecon Loop)

> [!IMPORTANT]
> ## Credits
> Original Discovery & Tool by: [5ec1cff](https://github.com/5ec1cff)\
> Based on the research regarding init behavior on `Android 11+` and failed SELinux context restoration.

## The Problem: Why your boot is slow
If you have a rooted device (especially with Kali Nethunter or massive number of files) and your boot time hangs on the first splash screen for minutes, you are likely stuck in a restorecon loop.

## Technical Explanation
During the `post-fs-data` stage of the boot process, the Android init binary performs a check on the `/data` partition. It tries to ensure all files have the correct SELinux labels.

- The Optimization: To avoid scanning millions of files every boot, Android calculates a hash based on the system's file contexts. If a scan completes successfully, it saves this hash into an extended attribute (`xattr`) on the `/data` folder called `security.sehash`.
- The Check: On the next boot, init compares the current system hash with the one stored in `security.sehash`. If they match, it skips the scan.
- The Failure: On some ROMs or heavy setups (like Nethunter), the `restorecon` process often fails mid-way (due to timeout, permission errors, or massive file counts in chroots).
- The Loop: Because it fails, the hash is never written. Consequently, every single time you reboot, Android thinks it's a "fresh" update and tries to relabel every file in your Nethunter chroot again. This causes massive I/O wait and delays boot by minutes.

## The Solution
The [restorehash](https://github.com/nullptr-t-oss/EmberHeart_OnePlus11/raw/refs/heads/main/tools/restorehash) tool automates a workaround. Instead of letting the system fail repeatedly, it calculates the correct hash in a safe environment and forces it onto the `/data` directory.

## Installation & Usage

### Prerequisites
- Termux (in root shell) or Android Root Shell (Nethunter Terminal)
- The [restorehash](https://github.com/nullptr-t-oss/EmberHeart_OnePlus11/raw/refs/heads/main/tools/restorehash) binary

### Step-by-Step Guide
- Place the Binary: Move the `restorehash` file to `/data/local/`

```
su
cp /sdcard/Download/restorehash /data/local/
```

- Set Permissions:  Give the binary executable permissions.

```
cd /data/local
chmod 777 restorehash
```

- Run the Fix: Execute the tool with the restore argument.

```
./restorehash restore
```

- Verify: If successful, the tool will update the security.sehash attribute. Reboot your device. The boot time should now be significantly faster (skipping the massive file scan)