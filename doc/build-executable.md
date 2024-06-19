<h1 align=center>Executable Build Guide</h1>

Welcome! This comprehensive guide will walk you through the steps to manually build FiSE into an executable file. The procedure is consistent across all platforms, with minor variations detailed below.

### Prerequisites

1. **Source Code**: Ensure you have the FiSE source code downloaded from the **GitHub Repository** on your system.

2. **Dependencies**: Install the necessary dependencies for running the application. Additional dependencies may also be installed for accessing optional features such as exporting records to SQL databases.

**For detailed instructions on installing these prerequisites, refer to the [Getting-Started](./getting-started.md) Guide.**

### Installing Pyinstaller

After installing the prerequisites, you need to install pyinstaller to build the executable file. To do so, run the following command:

```bash
python -m pip install pyinstaller --no-cache
```

### Building the Executable

Once you have installed `pyinstaller`, you can build finally build the executable using the following command below:

```bash
pyinstaller --onefile fise/main.py
```

**NOTE: Before running the above command, you must ensure that you have set the current working directory to the source code directory.**

This command works the same for all platforms, and will generate an executable file which can run on the current platform.

### Running the Executable

After the build process is complete, navigate to the `dist` directory generated automatically by `pyinstaller` within the source code directory. Inside, you will find the generated executable file ready to be executed.

---
