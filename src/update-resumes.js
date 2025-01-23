import { execSync } from 'child_process';
import fs from 'fs';
const {
  PDF_URL_EN,
  PDF_URL_ES,
  USER_NAME,
  USER_EMAIL
} = process.env;

const URLS = [PDF_URL_EN, PDF_URL_ES];

async function downloadPDF(pdfURL, outputFilename) {
    let pdfBuffer = await request.get({uri: pdfURL, encoding: null});
    console.log("Writing downloaded PDF file to " + outputFilename + "...");
    fs.writeFileSync(outputFilename, pdfBuffer);
}

const downloadAndUpdatePDFs = async () => {
  let changed = false;
  let PDF_DIR = './pdfs';
  // Ensure the PDF_DIR exists
  try {
    await fs.promises.access(PDF_DIR);
  } catch {
    await fs.promises.mkdir(PDF_DIR, { recursive: true });
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
      downloadPDF(url, filePath);
    }
    catch (err) {
      console.error('Error downloading PDF:', err);
      process.exit(1);
    }
    fs.writeFile(filePath, file);
  }
  
    execSync(`git config --global user.name '${USER_NAME}'`);
    execSync(`git config --global user.email '${USER_EMAIL}'`);
    execSync(`git add ${PDF_DIR}/*.pdf`);
    execSync(`git commit -m "📄 PDF Update [${new Date().toISOString()}] - Successfully updated resume files"`);
    execSync('git push');
};

downloadAndUpdatePDFs();
