# Porting OnePlus Nethunter Kernel to New Devices

This guide explains how to add support for a new OnePlus device (e.g., OnePlus 12, Open, Nord series) to the EmberHeart Kernel CI/CD pipeline.

First star this repo, create a fork and follow the instructions given below.

## 1. Prerequisites
To port a new device, you need three pieces of information from the [OnePlusOSS GitHub](https://github.com/OnePlusOSS):
1.  **Device Model Code** (e.g., `OP12`, `OPOpen`).
2.  **SoC Codename** (e.g., `kalama` for SD 8 Gen 2, `pineapple` for SD 8 Gen 3).
3.  **Source Branch** and **Manifest XML** names.

## 2. Create the Configuration File
The workflow automatically scans the `configs/` directory. To add a device, simply create a new `.json` file in that folder (e.g., `configs/OP12.json`).

### JSON Structure Explanation
Copy the structure below and modify the values for your target device.

```json
{
  "model": "OP12",
  "soc": "pineapple",
  "branch": "oneplus/sm8650",
  "manifest_oos14": "oneplus_12_u.xml",
  "manifest_oos14_modules": "oneplus_12_u.xml",
  "manifest_oos15": "oneplus_12_v.xml",
  "manifest_oos15_modules": "oneplus_12_v.xml",
  "manifest_fast_build_oos15": "https://raw.githubusercontent.com/nullptr-t-oss/kernel_patches/refs/heads/main/kernel_manifest/oneplus_12_v_kernel.xml",
  "manifest_fast_build_oos15_modules": "https://raw.githubusercontent.com/nullptr-t-oss/kernel_patches/refs/heads/main/kernel_manifest/oneplus_12_v_modules.xml",
  "manifest_oos16": "oneplus_12_b.xml",
  "manifest_oos16_modules": "oneplus_12_b.xml",
  "android_version": "android14",
  "kernel_version": "6.1",
  "hmbird": false
}
```

### Parameter Breakdown
*   **`model`**: A short identifier for the device (used for file naming).
*   **`soc`**: The chipset codename.
    *   *Examples:* `kalama` (SD8Gen2), `pineapple` (SD8Gen3), `taro` (SD8Gen1).
*   **`branch`**: The git branch on OnePlusOSS containing the kernel source.
*   **`manifest_...`**: The specific XML filename inside the `kernel_manifest` repo for that Android version.
    *   `manifest_oos15`: Standard full source manifest.
    *   `manifest_fast_build_...`: (Optional) A custom trimmed manifest URL if you want to speed up `repo sync` by removing unnecessary git history or projects. If you don't have one, just use the filename from the standard manifest (e.g., `"oneplus_12_v.xml"`).
*   **`android_version`**: The base Android version the kernel is built on (e.g., `android14`).
*   **`kernel_version`**: The Linux kernel version (e.g., `6.1`).

## 3. Handle Device-Specific Patches (Optional)
The workflow logic (`actions/action.yml`) applies patches based on the SoC.

### Scenario A: Your device shares an SoC with an existing device
If you are adding a device with the same SoC (e.g., `kalama` like the OnePlus 11), the workflow will automatically attempt to apply patches located in:
`my_patches/kernel_patches/op11/common/*.patch` (as seen in `actions/action.yml`)

*Check the workflow logic:*
```yaml
- name: Add my kernel patches to common kernel
  if: env.OP_SOC == 'kalama'
```
> [!NOTE]
> You may need to remove some of patches if the build is failing.

### Scenario B: New SoC (e.g., Snapdragon 8 Gen 3)
1.  **Repository Setup:** You need to fork or update the repository `nullptr-t-oss/kernel_patches`.
2.  **Directory Structure:** Create a folder for your new device/SoC patches.
3.  **Workflow Update:** Edit `actions/action.yml` and `kernel_modules/action.yml` to include your new SoC.

**In `actions/action.yml` (Search for "Add my kernel patches"):**
```yaml
    - name: Add my kernel patches to common kernel
      if: env.OP_SOC == 'pineapple'  <-- Add your SoC here
      shell: bash
      run: |
        set -euo pipefail
        # Update path to point to your new patches
        for patch_file in ../../../my_patches/kernel_patches/op12/common/*.patch; do
            patch -p1 < "$patch_file"
        done
```

**In `kernel_modules/action.yml` (Search for "Add my kernel patches"):**
```yaml
    - name: Add my kernel patches to msm kernel
      if: env.OP_SOC == 'pineapple'  <-- Add your SoC here
      run: |
        # Update path to point to your new module patches
        for patch_file in ../../../my_patches/kernel_patches/op12/msm/*.patch; do
            patch -p1 < "$patch_file"
        done
```

## 4. Nethunter & Driver Customization
The Nethunter configuration is **device-agnostic** for the most part, as the workflow injects the necessary config flags directly into `gki_defconfig`.

### How it works:
1.  **Kernel Integration (`actions/action.yml`):** Adds support for USB extensions, SDR (AirSpy, HackRF), and Bluetooth HCI.
2.  **Wireless Modules (`kernel_modules/action.yml`):** Enables Wi-Fi drivers (ATH9K, MT76, RTL88XX) as **modules** (`=m`).

**Do I need to change anything?**
*   **No:** If you just want standard Nethunter support (External Wi-Fi injection, HID attacks).
*   **Yes:** If you need a specific driver that is not added to this repo already.

## 5. Build Execution
Once the `configs/YOUR_DEVICE.json` is created:

1.  Go to the **Actions** tab in GitHub.
2.  Select **"Build and Release OnePlus EmberHeart Kernel..."**.
3.  Click **Run workflow**.
4.  **Model:** The dropdown defaults to `OP11`. Since you added a new JSON file, the `set-op-model` job at the start of the workflow will detect your config file, but you may need to type the model name manually if the UI dropdown hasn't updated, or simply rely on the matrix build if you select "All" (logic modification required for "All" selection, otherwise simply type the filename key).
    *   *Note on UI:* The current workflow inputs restrict choice to `OP11`. You should update the `build-kernel-release.yml` inputs section to include your new model:
    ```yaml
      model:
        description: 'Select device to be built'
        required: true
        type: choice
        options:
          - OP11
          - OP12   <-- Add your new model here
    ```

## 6. Troubleshooting Common Porting Issues

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `repo sync` fails | Incorrect manifest name or branch | Verify the filename in `configs/OPxx.json` exactly matches the file in [OnePlusOSS/kernel_manifest](https://github.com/OnePlusOSS/kernel_manifest). |
| Build fails at patching | Patch mismatch | The patches in `my_patches` might be specific to Android 13/14. If porting to Android 15, some patches (like `task_mmu.c` fixes) may need manual adjustment. |
