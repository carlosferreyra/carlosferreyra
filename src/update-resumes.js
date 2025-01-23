import { execSync } from 'child_process';
import { promises as fs } from 'fs';
import fetch from 'node-fetch';

const {
  PDF_URL_EN,
  PDF_URL_ES,
  USER_NAME,
  USER_EMAIL
} = process.env;

const URLS = [PDF_URL_EN, PDF_URL_ES];

const downloadAndUpdatePDFs = async () => {
  let changed = false;
  let PDF_DIR = './pdfs';
  // Ensure the PDF_DIR exists
  try {
    await fs.access(PDF_DIR);
  } catch {
    await fs.mkdir(PDF_DIR, { recursive: true });
  }

  let name;
  try {
    const data = await fs.readFile('./package.json', 'utf8');
    name = JSON.parse(data).name;
  } catch (err) {
    console.error('Error reading package.json:', err);
    process.exit(1);
  }

  for (let i = 0; i < URLS.length; i++) {
    const url = URLS[i];
    const filename = `${name.replace(" ","-")}-${i === 0 ? 'en' : 'es'}.pdf`;
    const filePath = `${PDF_DIR}/${filename}`;

    try {
      // Download the PDF
      const response = await fetch(url);
      if (response.status !== 200) {
        console.error(`Failed to download PDF from ${url} (HTTP ${response.status})`);
        process.exit(1);
      }
      const pdf = await response.buffer();
      // save the PDF to the file system, overwriting the old file
      await fs.writeFile(filePath, pdf);
    } catch (error) {
      console.error(`Error downloading PDF: ${error}`);
      process.exit(1);
    }
  }
  changed = true;
  if (changed) {
    console.log("Changes detected in PDFs. Proceeding with git operations...");
    execSync(`git config --global user.name '${USER_NAME}'`);
    execSync(`git config --global user.email '${USER_EMAIL}'`);
    execSync(`git add ${PDF_DIR}/*.pdf`);
    execSync(`git commit -m "📄 PDF Update [${new Date().toISOString()}] - Successfully updated resume files"`);
    execSync('git push');
  } else {
    console.log("No changes detected in PDFs. Workflow completed successfully.");
  }
};

downloadAndUpdatePDFs();
