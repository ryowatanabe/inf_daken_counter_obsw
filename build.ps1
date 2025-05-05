# PowerShell script to replicate the functionality of build.sh

# Path to PyInstaller
$pyin = "pyinstaller"

# Run PyInstaller to build the executable
& $pyin "notes_counter.pyw" --clean --noconsole --onefile --icon="icon.ico" --add-data "icon.ico;./" --add-data "resources/*;./resources/" --add-data "export/*;./export/"

# Copy the built executable and other necessary files to the target directories
Copy-Item -Path "dist/notes_counter.exe" -Destination "inf_daken_counter" -Force
Copy-Item -Path "version.txt" -Destination "inf_daken_counter/" -Force
Copy-Item -Path "noteslist.pkl" -Destination "inf_daken_counter/" -Force
Copy-Item -Path "dp_unofficial.pkl" -Destination "inf_daken_counter/" -Force
Copy-Item -Path "sp_12jiriki.pkl" -Destination "inf_daken_counter/" -Force

# Copy directories recursively
Copy-Item -Path "layout" -Destination "inf_daken_counter/" -Recurse -Force
Copy-Item -Path "resources" -Destination "inf_daken_counter/" -Recurse -Force

# Create a ZIP archive of the target directory
Compress-Archive -Path "inf_daken_counter/*", "inf_daken_counter/*/*", "inf_daken_counter/*/*/*" -DestinationPath "inf_daken_counter.zip" -Force