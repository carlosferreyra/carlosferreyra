import axios from 'axios';
import fs from 'fs';
import path from 'path';

async function updatePackageJson() {
    const packageJsonPath = path.resolve('package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
    const repoUrl = `https://api.github.com/repos/carlosferreyra/${packageJson.name}`;

    try {
        const response = await axios.get(repoUrl);
        const repoInfo = response.data;

        let updated = false;

        console.log('Fetched license:', repoInfo.license.name);
        if (packageJson.license !== repoInfo.license.name) {
            packageJson.license = repoInfo.license.name;
            updated = true;
        }

        console.log('Fetched author name:', repoInfo.owner.login);
        if (packageJson.author.name !== repoInfo.owner.login) {
            packageJson.author.name = repoInfo.owner.login;
            updated = true;
        }

        console.log('Fetched description:', repoInfo.description);
        if (packageJson.description !== repoInfo.description) {
            packageJson.description = repoInfo.description;
            updated = true;
        }

        const repoKeywords = repoInfo.topics;
        console.log('Fetched keywords:', repoKeywords);
        if (JSON.stringify(packageJson.keywords) !== JSON.stringify(repoKeywords)) {
            packageJson.keywords = repoKeywords;
            updated = true;
        }

        if (updated) {
            fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
            console.log('package.json updated successfully');
        } else {
            console.log('No changes needed for package.json');
        }
    } catch (error) {
        console.error('Error fetching repo info:', error);
    }
}

updatePackageJson();
