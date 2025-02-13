import { execSync } from 'child_process';
import fs from 'fs';
import https from 'https';
import { google } from 'googleapis';

// Set default user credentials for local development
let USER_NAME = process.env.USER_NAME || 'Carlos Ferreyra';
let USER_EMAIL = process.env.USER_EMAIL || 'eduferreyraok@gmail.com';

const {
  GOOGLE_DRIVE_API_KEY,
  GOOGLE_DRIVE_FOLDER_ID
} = process.env;

const BASE_URL = "https://storage.rxresu.me/clz62ydvs5a9cvrn3hvbh93tp/resumes/";
const pdf = "carlos-ferreyra.pdf";
const pdf_es = "carlos-ferreyra-espanol.pdf";

const URLS = [BASE_URL + pdf, BASE_URL + pdf_es];
const PDF_DIR = './pdfs';

async function downloadPDF(pdfURL, outputFilename) {
  console.log(`Downloading PDF from URL: ${pdfURL} to ${outputFilename}`);
  return new Promise((resolve, reject) => {
    https.get(pdfURL, (response) => {
      if (response.statusCode !== 200) {
        const errorMessage = `Failed to get '${pdfURL}' (${response.statusCode})`;
        console.error(errorMessage);
        reject(new Error(errorMessage));
        return;
      }
      const file = fs.createWriteStream(outputFilename);
      response.pipe(file);
      file.on('finish', () => {
        file.close(resolve);
        console.log(`Successfully downloaded PDF file to ${outputFilename}`);
      });
    }).on('error', (err) => {
      console.error(`Error during PDF download from ${pdfURL}:`, err.message);
      fs.unlink(outputFilename, () => { /* ignore unlink error */ }); // Best effort cleanup
      reject(err);
    });
  });
}

async function setupGoogleDrive() {
  if (!GOOGLE_DRIVE_API_KEY) {
    throw new Error('GOOGLE_DRIVE_API_KEY environment variable is not set');
  }

  const auth = new google.auth.GoogleAuth({
    credentials: JSON.parse(GOOGLE_DRIVE_API_KEY),
    scopes: ['https://www.googleapis.com/auth/drive.file']
  });
  return google.drive({ version: 'v3', auth });
}

async function uploadToDrive(drive, filePath, fileName) {
  try {
    const folderId = GOOGLE_DRIVE_FOLDER_ID;
    if (!folderId) {
      throw new Error('GOOGLE_DRIVE_FOLDER_ID environment variable is not set');
    }

    // Check for and delete existing file
    const response = await drive.files.list({
      q: `name='${fileName}' and '${folderId}' in parents and trashed=false`,
      fields: 'files(id)'
    });

    if (response.data.files.length > 0) {
      const existingFileId = response.data.files[0].id;
      await drive.files.delete({ fileId: existingFileId });
    }

    // Upload new file
    const fileMetadata = {
      name: fileName,
      parents: [folderId]
    };
    const media = {
      mimeType: 'application/pdf',
      body: fs.createReadStream(filePath)
    };

    const uploadResponse = await drive.files.create({
      resource: fileMetadata,
      media: media,
      fields: 'id'
    });

    return uploadResponse.data.id;
  } catch (error) {
    console.error(`Upload failed for ${fileName}:`, error.message);
    throw error;
  }
}

const downloadAndUpdatePDFs = async () => {
  console.log('Starting PDF download and update process...');

  // Ensure the PDF_DIR exists
  if (!fs.existsSync(PDF_DIR)) {
    console.log(`PDF directory '${PDF_DIR}' does not exist. Creating it...`);
    fs.mkdirSync(PDF_DIR);
    console.log(`PDF directory '${PDF_DIR}' created successfully.`);
  }

  let packageName = 'default-package-name'; // Default name if package.json read fails
  try {
    const data = await fs.promises.readFile('./package.json', 'utf8');
    packageName = JSON.parse(data).name;
  } catch (err) {
    console.warn('Warning: Error reading package.json. Using default package name.', err.message);
  }

  // Initialize Google Drive
  let drive;
  try {
    drive = await setupGoogleDrive();
  } catch (error) {
    console.error('Google Drive setup failed. Aborting PDF update process.');
    process.exit(1);
  }

  for (let i = 0; i < URLS.length; i++) {
    const url = URLS[i];
    let fmtName = packageName[0].toUpperCase() + packageName.slice(1);
    fmtName = fmtName.replace('sf', 's-F');
    const filename = `${fmtName}${i === 0 ? '-en' : '-es'}.pdf`;
    const filePath = `${PDF_DIR}/${filename}`;

    try {
      await downloadPDF(url, filePath);
      await uploadToDrive(drive, filePath, filename);
    } catch (err) {
      console.error(`Error processing PDF from URL ${url}:`, err);
      console.error('Aborting PDF update process due to errors.');
      process.exit(1);
    }
  }

  console.log('PDF downloads and Google Drive uploads completed successfully.');

  console.log('Configuring git user...');
  execSync(`git config --global user.name '${USER_NAME}'`);
  execSync(`git config --global user.email '${USER_EMAIL}'`);
  console.log('Git user configured.');

  console.log("Checking for changes before commit...");
  const hasChanges = execSync('git status --porcelain').toString();

  if (hasChanges) {
    const commitMessage = `📄 PDF Update [${new Date().toISOString()}] - Successfully updated resume files and backed up to Google Drive`;
    console.log('Changes detected. Adding, committing and pushing...');
    execSync('git add .');
    execSync(`git commit -m "${commitMessage}"`);
    console.log('Changes committed with message:', commitMessage);
    try {
      execSync('git push');
      console.log('Changes pushed to repository.');
    } catch (pushError) {
      console.error('Error pushing changes to repository:', pushError.message);
      console.error('Please check the workflow permissions and repository settings.');
    }

  } else {
    console.log('No changes to commit to repository.');
  }

  console.log('PDF Update and Google Drive Backup process finished.');
};

downloadAndUpdatePDFs();