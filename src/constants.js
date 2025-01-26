import fs from 'fs/promises';
// import { PLACEHOLDERS } from './constants.js';
const PLACEHOLDERS = {
    USER: await fs.readFile('./package.json', { encoding: 'utf-8' }).then(data => JSON.parse(data).name),
    USER_ORGS: 'https://api.github.com/user/orgs', // the user needs to be authenticated to get all the orgs and have org:read scope
    USER_API_URL: 'https://api.github.com/users/<user>/repos',
    ORGS_API_URL: 'https://api.github.com/orgs/<org>/repos',
    REPOS: '%{{REPOS}}',
    PROJECTS: '%{{PROJECTS}}',
}

const PDF_DIRECTORY = './pdfs';

export { PLACEHOLDERS, PDF_DIRECTORY };
