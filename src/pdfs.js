import { execSync } from 'child_process';
import fs from 'fs';
const {
  USER_NAME,
  USER_EMAIL
} = process.env;
//"https://storage.rxresu.me/clz62ydvs5a9cvrn3hvbh93tp/resumes/carlos-ferreyra.pdf"
//"https://storage.rxresu.me/clz62ydvs5a9cvrn3hvbh93tp/resumes/carlos-ferreyra-espanol.pdf"
const BASE_URL = "https://storage.rxresu.me/clz62ydvs5a9cvrn3hvbh93tp/resumes/";
const pdf = "carlos-ferreyra.pdf"
const pdf_es = "carlos-ferreyra-espanol.pdf"

const URLS = [BASE_URL + pdf, BASE_URL + pdf_es];

import https from 'https';

async function downloadPDF(pdfURL, outputFilename) {
  return new Promise((resolve, reject) => {
    https.get(pdfURL, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to get '${pdfURL}' (${response.statusCode})`));
        return;
      }
      const file = fs.createWriteStream(outputFilename);
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
        console.log("Writing downloaded PDF file to " + outputFilename + "...");
      });
    }).on('error', (err) => {
      console.error('Error on PDF:', err);
      fs.unlink(outputFilename);
      reject(err);
    });
  });
}

const downloadAndUpdatePDFs = async () => {
  let PDF_DIR = './pdfs';
  // Ensure the PDF_DIR exists

  let name;
  try {
    const data = await fs.promises.readFile('./package.json', 'utf8');
    name = JSON.parse(data).name;
  } catch (err) {
    console.error('Error reading package.json:', err);
    process.exit(1);
  }

  for (let i = 0; i < URLS.length; i++) {
    const url = URLS[i];
    let fmtName = name[0].toUpperCase() + name.slice(1);
    fmtName = fmtName.replace('sf', 's-F');
    const filename = `${fmtName}${i === 0 ? '' : '-es'}.pdf`;
    const filePath = `${PDF_DIR}/${filename}`;

    try {

      await downloadPDF(url, filePath)
      // Download the PD
    }
    catch (err) {
      console.error('Error processing PDF:', err);
      process.exit(1);
    }
  }

  execSync(`git config --global user.name '${USER_NAME}'`);
  execSync(`git config --global user.email '${USER_EMAIL}'`);
  console.log("Committing and pushing changes to the repo...");
  execSync(`echo $GITHUB_CONTEXT`)


  const commitMessage = `📄 PDF Update [${new Date().toISOString()}] - Successfully updated resume files`;
  // Check if there are changes before committing
  const hasChanges = execSync('git status --porcelain').toString();
  if (hasChanges) {
    execSync('git add .');
    execSync(`git commit -m "${commitMessage}"`);
  } else {
    console.log('No changes to commit');
  }

  execSync('git push');
};

downloadAndUpdatePDFs();
