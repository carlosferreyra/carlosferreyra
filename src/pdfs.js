import { execSync } from 'child_process';
import fs from 'fs';
import https from 'https';
import { google } from 'googleapis';

const {
  USER_NAME,
  USER_EMAIL,
  GOOGLE_DRIVE_API_KEY,
  GOOGLE_DRIVE_FOLDER_ID
} = process.env;

const BASE_URL = "https://storage.rxresu.me/clz62ydvs5a9cvrn3hvbh93tp/resumes/";
const pdf = "carlos-ferreyra.pdf"
const pdf_es = "carlos-ferreyra-espanol.pdf"

const URLS = [BASE_URL + pdf, BASE_URL + pdf_es];

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

async function setupGoogleDrive() {
  try {
    if (!GOOGLE_DRIVE_API_KEY) {
      throw new Error('GOOGLE_DRIVE_API_KEY environment variable is not set');
    }

    const auth = new google.auth.GoogleAuth({
      credentials: JSON.parse(GOOGLE_DRIVE_API_KEY),
      scopes: ['https://www.googleapis.com/auth/drive.file']
    });
    return google.drive({ version: 'v3', auth });
  } catch (error) {
    console.error('Error setting up Google Drive:', error.message);
    throw error;
  }
}

async function uploadToDrive(drive, filePath, fileName) {
  try {
    const folderId = GOOGLE_DRIVE_FOLDER_ID;
    if (!folderId) {
      throw new Error('GOOGLE_DRIVE_FOLDER_ID environment variable is not set');
    }
    
    // Search for existing file in the specified folder
    const response = await drive.files.list({
      q: `name='${fileName}' and '${folderId}' in parents and trashed=false`,
      fields: 'files(id)'
    }).catch(err => {
      console.error('Error listing files:', err.message);
      throw err;
    });

    // Delete existing file if found
    if (response.data.files.length > 0) {
      try {
        await drive.files.delete({
          fileId: response.data.files[0].id
        });
      } catch (deleteErr) {
        // If deletion fails, log it but continue with upload
        console.warn(`Warning: Could not delete existing file: ${deleteErr.message}`);
      }
    }

    // Upload new file to the specified folder
    const fileMetadata = {
      name: fileName,
      parents: [folderId]
    };
    const media = {
      mimeType: 'application/pdf',
      body: fs.createReadStream(filePath)
    };

    const uploadResponse = await drive.files.create({
      requestBody: fileMetadata,
      media: media,
      fields: 'id'
    }).catch(err => {
      console.error('Error uploading file:', err.message);
      throw err;
    });

    console.log(`Successfully uploaded ${fileName} to Google Drive folder ${folderId} with file ID: ${uploadResponse.data.id}`);
  } catch (error) {
    console.error(`Failed to process file ${fileName}:`, error);
    throw error;
  }
}


const downloadAndUpdatePDFs = async () => {
  let PDF_DIR = './pdfs';
  // Ensure the PDF_DIR exists
  if (!fs.existsSync(PDF_DIR)) {
    fs.mkdirSync(PDF_DIR);
  }

  let name;
  try {
    const data = await fs.promises.readFile('./package.json', 'utf8');
    name = JSON.parse(data).name;
  } catch (err) {
    console.error('Error reading package.json:', err);
    process.exit(1);
  }

  // Initialize Google Drive
  const drive = await setupGoogleDrive();

  for (let i = 0; i < URLS.length; i++) {
    const url = URLS[i];
    let fmtName = name[0].toUpperCase() + name.slice(1);
    fmtName = fmtName.replace('sf', 's-F');
    const filename = `${fmtName}${i === 0 ? '-en' : '-es'}.pdf`;
    const filePath = `${PDF_DIR}/${filename}`;

    try {
      await downloadPDF(url, filePath);
      // Upload to Google Drive
      await uploadToDrive(drive, filePath, filename);
    } catch (err) {
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
