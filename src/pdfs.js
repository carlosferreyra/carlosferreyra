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
  const auth = new google.auth.GoogleAuth({
    credentials: JSON.parse(GOOGLE_DRIVE_API_KEY),
    scopes: ['https://www.googleapis.com/auth/drive.file']
  });
  return google.drive({ version: 'v3', auth });
}

async function uploadToDrive(drive, filePath, fileName) {
  // Get or create Resumes folder
  let folderId;
  const folderResponse = await drive.files.list({
    q: "name='Resumes' and mimeType='application/vnd.google-apps.folder' and 'root' in parents and trashed=false",
    fields: 'files(id)'
  });

  if (folderResponse.data.files.length > 0) {
    folderId = folderResponse.data.files[0].id;
  } else {
    const folderMetadata = {
      name: 'Resumes',
      mimeType: 'application/vnd.google-apps.folder',
      parents: ['root']
    };
    const folder = await drive.files.create({
      requestBody: folderMetadata,
      fields: 'id'
    });
    folderId = folder.data.id;
  }

  // Search for existing file in Resumes folder
  const response = await drive.files.list({
    q: `name='${fileName}' and '${folderId}' in parents and trashed=false`,
    fields: 'files(id)'
  });

  // Delete existing file if found
  if (response.data.files.length > 0) {
    await drive.files.delete({
      fileId: response.data.files[0].id
    });
  }

  // Upload new file to Resumes folder
  const fileMetadata = {
    name: fileName,
    parents: [folderId]
  };
  const media = {
    mimeType: 'application/pdf',
    body: fs.createReadStream(filePath)
  };

  await drive.files.create({
    requestBody: fileMetadata,
    media: media,
    fields: 'id'
  });
  console.log(`Successfully uploaded ${fileName} to Google Drive in Resumes folder`);
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
