import { execSync } from 'child_process';
import fs from 'fs';
const {
  PDF_URL_EN,
  PDF_URL_ES,
  USER_NAME,
  USER_EMAIL
} = process.env;

const URLS = [PDF_URL_EN, PDF_URL_ES];

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
    const filename = `${name}-${i === 0 ? 'en' : 'es'}.pdf`;
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
    execSync(`git add ${PDF_DIR}/*.pdf`);
    execSync(`echo $GITHUB_CONTEXT`)
    execSync(`git commit -m "📄 PDF Update [${new Date().toISOString()}] - Successfully updated resume files"`);
    execSync('git push');
};

downloadAndUpdatePDFs();
