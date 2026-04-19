const fs = require('fs');
const https = require('https');
const { execSync } = require('child_process');

const url = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/MinGit-2.44.0-64-bit.zip";
const dest = "mingit.zip";

console.log("Downloading MinGit via Node...");
const file = fs.createWriteStream(dest);

https.get(url, (response) => {
    if (response.statusCode === 302) {
        https.get(response.headers.location, (res2) => {
            res2.pipe(file);
            file.on('finish', () => {
                file.close(() => {
                    console.log("Download complete. Extracting via powershell...");
                    try {
                        execSync('powershell.exe -Command "Expand-Archive -Path mingit.zip -DestinationPath portable_git -Force"', {stdio: 'inherit'});
                        console.log("Extracted to /portable_git. Ready.");
                    } catch (e) {
                        console.error("Shell extraction failed:", e.message);
                    }
                });
            });
        }).on('error', (err) => { fs.unlink(dest); console.error(err); });
    } else {
        response.pipe(file);
        // ...
    }
}).on('error', (err) => { 
    fs.unlink(dest); 
    console.error(err); 
});
