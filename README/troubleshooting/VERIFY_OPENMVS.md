# Verify OpenMVS Installation

## Quick Verification Commands

After OpenMVS build completes, verify installation:

```bash
# Check if binaries exist
ls -la /usr/local/bin/OpenMVS/

# Test DensifyPointCloud
/usr/local/bin/OpenMVS/DensifyPointCloud --help | head -5

# Test InterfaceCOLMAP
/usr/local/bin/OpenMVS/InterfaceCOLMAP --help | head -5

# Check symlinks (if created)
ls -la /usr/local/bin/ | grep -E "DensifyPointCloud|InterfaceCOLMAP"

# Verify PATH includes OpenMVS
echo $PATH | grep OpenMVS
```

## Expected Output

You should see:
- ✅ All binaries in `/usr/local/bin/OpenMVS/`
- ✅ `DensifyPointCloud --help` shows usage
- ✅ `InterfaceCOLMAP --help` shows usage
- ✅ Symlinks created in `/usr/local/bin/` (if script ran successfully)

## If Verification Fails

If the verification step fails but binaries exist:

```bash
# Manually create symlinks
OPENMVS_BIN="/usr/local/bin/OpenMVS"
for tool in DensifyPointCloud InterfaceCOLMAP ReconstructMesh; do
    ln -sf "${OPENMVS_BIN}/${tool}" "/usr/local/bin/${tool}"
done

# Add to PATH
export PATH="/usr/local/bin/OpenMVS:$PATH"
echo 'export PATH="/usr/local/bin/OpenMVS:$PATH"' >> ~/.bashrc

# Verify again
DensifyPointCloud --help | head -3
```
