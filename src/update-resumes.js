import { execSync } from 'child_process';
import { promises as fs } from 'fs';

const {
  PDF_RESUME_URL,
  PDF_RESUME_ES_URL,
  PDF_DIR,
  PDF_EN_FILENAME,
  PDF_ES_FILENAME,
  USER_NAME,
  USER_EMAIL
} = process.env;

const URLS = [PDF_RESUME_URL, PDF_RESUME_ES_URL];
const FILENAMES = [PDF_EN_FILENAME, PDF_ES_FILENAME];

const downloadAndUpdatePDFs = async () => {
  let changed = false;

  // Ensure the PDF_DIR exists
  await fs.mkdir(PDF_DIR, { recursive: true });

  for (let i = 0; i < URLS.length; i++) {
    const url = URLS[i];
    const filename = FILENAMES[i];
    const filePath = `${PDF_DIR}/${filename}`;

    try {
      const response = await fetch(url);
      if (response.status !== 200) {
        console.error(`Failed to download PDF from ${url} (HTTP ${response.status})`);
        process.exit(1);
      }

      // Convert ArrayBuffer to Buffer
      const arrayBuffer = await response.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      await fs.writeFile(filePath, buffer);

      // Compare with existing file using full path
      const fileExists = await fs.access(filePath).then(() => true).catch(() => false);
      if (!fileExists) {
        changed = true;
      } else {
        const existingFile = await fs.readFile(filePath);
        const newFile = buffer;
        changed = !existingFile.equals(newFile);
      }
    } catch (error) {
      console.error(`Error downloading or comparing PDF: ${error}`);
      process.exit(1);
    }
  }

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
