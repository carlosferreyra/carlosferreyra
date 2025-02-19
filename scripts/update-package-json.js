import axios from 'axios';
import fs from 'fs';
import path from 'path';

async function updatePackageJson() {
    const packageJsonPath = path.resolve('package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf-8'));
    const userHandler = 'carlosferreyra'; // Change this to your GitHub username
    const repoHandler = packageJson.name
    const repoUrl = `https://api.github.com/repos/${userHandler}/${repoHandler}`;
    try {
        const response = await axios.get(repoUrl);
        const repoInfo = response.data;
        const userUrl = `https://api.github.com/users/${userHandler}`;
        const owner = await axios.get(userUrl);
        const ownerInfo = owner.data;

        let updated = false;

        console.log('Fetched license:', repoInfo.license.spdx_id);
        if (packageJson.license !== repoInfo.license.spdx_id) {
            packageJson.license = repoInfo.license.spdx_id;
            updated = true;
        }

        console.log('Fetched author:', ownerInfo.name);
        const authorData = {
            name: ownerInfo.name || repoInfo.owner.login,
            email: ownerInfo.email || undefined
        };

        if (JSON.stringify(packageJson.author) !== JSON.stringify(authorData)) {
            packageJson.author = authorData;
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
