import { execSync } from 'child_process';
import crypto from 'crypto';
import fs from 'fs';
import { google } from 'googleapis';
import https from 'https';

// Set default user credentials for local development
let USER_NAME = process.env.USER_NAME || 'Carlos Ferreyra';
let USER_EMAIL = process.env.USER_EMAIL || 'eduferreyraok@gmail.com';

const { GOOGLE_DRIVE_API_KEY, GOOGLE_DRIVE_ROOT_FOLDER_ID } = process.env;

// Configuration - now path-based instead of hardcoded folder ID
const DRIVE_CONFIG = {
	rootFolderId: GOOGLE_DRIVE_ROOT_FOLDER_ID, // This should be your "Home" folder ID
	targetPath: 'Resumes', // Path from root: Home/Resumes
	// Alternative examples:
	// targetPath: 'Documents/PDFs'  // for Home/Documents/PDFs
	// targetPath: 'Work/Projects/Assets'  // for Home/Work/Projects/Assets
};

const BASE_URL = 'https://storage.rxresu.me/clz62ydvs5a9cvrn3hvbh93tp/resumes/';
const pdf = 'carlos-ferreyra.pdf';
const pdf_es = 'carlos-ferreyra-espanol.pdf';

const URLS = [BASE_URL + pdf, BASE_URL + pdf_es];
const PDF_DIR = './pdfs';

// Utility function to calculate file hash
function calculateFileHash(filePath) {
	const fileBuffer = fs.readFileSync(filePath);
	return crypto.createHash('sha256').update(fileBuffer).digest('hex');
}

// Utility function to get file stats
function getFileStats(filePath) {
	if (!fs.existsSync(filePath)) {
		return null;
	}
	const stats = fs.statSync(filePath);
	return {
		size: stats.size,
		modified: stats.mtime.toISOString(),
		hash: calculateFileHash(filePath),
	};
}

// Enhanced PDF download with debugging
async function downloadPDF(pdfURL, outputFilename) {
	console.log(`\n=== DOWNLOADING PDF ===`);
	console.log(`URL: ${pdfURL}`);
	console.log(`Output: ${outputFilename}`);
	console.log(`Timestamp: ${new Date().toISOString()}`);

	// Check if file exists before download
	const existingStats = getFileStats(outputFilename);
	if (existingStats) {
		console.log(`Existing file stats:`, existingStats);
	} else {
		console.log(`No existing file found at ${outputFilename}`);
	}

	// Add cache-busting parameter
	const cacheBustUrl = `${pdfURL}?cb=${Date.now()}`;
	console.log(`Cache-busted URL: ${cacheBustUrl}`);

	return new Promise((resolve, reject) => {
		https
			.get(cacheBustUrl, (response) => {
				console.log(`Response status: ${response.statusCode}`);
				console.log(`Response headers:`, JSON.stringify(response.headers, null, 2));

				if (response.statusCode !== 200) {
					const errorMessage = `Failed to get '${cacheBustUrl}' (${response.statusCode})`;
					console.error(errorMessage);
					reject(new Error(errorMessage));
					return;
				}

				const file = fs.createWriteStream(outputFilename);
				let downloadedBytes = 0;

				response.on('data', (chunk) => {
					downloadedBytes += chunk.length;
				});

				response.pipe(file);

				file.on('finish', () => {
					file.close(() => {
						console.log(`Download completed. Bytes downloaded: ${downloadedBytes}`);

						// Get new file stats
						const newStats = getFileStats(outputFilename);
						console.log(`New file stats:`, newStats);

						// Compare with existing file if it existed
						if (existingStats) {
							console.log(
								`File size changed: ${existingStats.size} -> ${newStats.size} (${
									newStats.size - existingStats.size
								} bytes difference)`
							);
							console.log(
								`File hash changed: ${existingStats.hash !== newStats.hash ? 'YES' : 'NO'}`
							);
							if (existingStats.hash === newStats.hash) {
								console.warn(`⚠️  WARNING: File hash is identical - content may not have changed!`);
							}
						}

						resolve();
					});
				});
			})
			.on('error', (err) => {
				console.error(`Error during PDF download from ${cacheBustUrl}:`, err.message);
				fs.unlink(outputFilename, () => {
					/* ignore unlink error */
				});
				reject(err);
			});
	});
}

async function setupGoogleDrive() {
	console.log(`\n=== SETTING UP GOOGLE DRIVE ===`);

	if (!GOOGLE_DRIVE_API_KEY) {
		throw new Error('GOOGLE_DRIVE_API_KEY environment variable is not set');
	}

	if (!GOOGLE_DRIVE_ROOT_FOLDER_ID) {
		throw new Error('GOOGLE_DRIVE_ROOT_FOLDER_ID environment variable is not set');
	}

	console.log(`Google Drive Root Folder ID: ${GOOGLE_DRIVE_ROOT_FOLDER_ID}`);
	console.log(`Target Path: ${DRIVE_CONFIG.targetPath}`);

	try {
		const credentials = JSON.parse(GOOGLE_DRIVE_API_KEY);
		console.log(`Credentials type: ${credentials.type}`);
		console.log(`Project ID: ${credentials.project_id}`);

		const auth = new google.auth.GoogleAuth({
			credentials: credentials,
			scopes: ['https://www.googleapis.com/auth/drive.file'],
		});

		const drive = google.drive({ version: 'v3', auth });

		// Test the connection
		console.log(`Testing Google Drive connection...`);
		const testResponse = await drive.about.get({ fields: 'user' });
		console.log(`Connected as: ${testResponse.data.user.emailAddress}`);

		return drive;
	} catch (error) {
		console.error(`Google Drive setup error:`, error);
		throw error;
	}
}

// NEW: Path-based folder navigation
async function findOrCreateFolderByPath(drive, baseFolderId, targetPath) {
	console.log(`\n=== NAVIGATING TO FOLDER PATH ===`);
	console.log(`Base Folder ID: ${baseFolderId}`);
	console.log(`Target Path: ${targetPath}`);

	const pathSegments = targetPath.split('/').filter((segment) => segment.trim() !== '');
	let currentFolderId = baseFolderId;

	console.log(`Path segments to navigate: ${JSON.stringify(pathSegments)}`);

	for (let i = 0; i < pathSegments.length; i++) {
		const folderName = pathSegments[i];
		console.log(`\n--- Looking for folder: ${folderName} ---`);

		try {
			// Search for folder in current directory
			const searchResponse = await drive.files.list({
				q: `name='${folderName}' and '${currentFolderId}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false`,
				fields: 'files(id, name)',
			});

			if (searchResponse.data.files.length > 0) {
				// Folder exists
				currentFolderId = searchResponse.data.files[0].id;
				console.log(`Found existing folder: ${folderName} (ID: ${currentFolderId})`);
			} else {
				// Create folder
				console.log(`Creating new folder: ${folderName}`);
				const createResponse = await drive.files.create({
					resource: {
						name: folderName,
						mimeType: 'application/vnd.google-apps.folder',
						parents: [currentFolderId],
					},
					fields: 'id, name',
				});

				currentFolderId = createResponse.data.id;
				console.log(`Created folder: ${folderName} (ID: ${currentFolderId})`);
			}
		} catch (error) {
			console.error(`Error handling folder ${folderName}:`, error);
			throw error;
		}
	}

	console.log(`\n✅ Successfully navigated to: ${targetPath} (Final ID: ${currentFolderId})`);
	return currentFolderId;
}

async function uploadToDrive(drive, filePath, fileName) {
	console.log(`\n=== UPLOADING TO GOOGLE DRIVE ===`);
	console.log(`Local file: ${filePath}`);
	console.log(`Drive file name: ${fileName}`);
	console.log(`Timestamp: ${new Date().toISOString()}`);

	try {
		// Get target folder ID using path navigation
		const targetFolderId = await findOrCreateFolderByPath(
			drive,
			DRIVE_CONFIG.rootFolderId,
			DRIVE_CONFIG.targetPath
		);

		// Get local file stats
		const localStats = getFileStats(filePath);
		console.log(`Local file stats:`, localStats);

		// Check for existing files in Google Drive
		console.log(`Searching for existing files named '${fileName}' in target folder...`);
		const searchResponse = await drive.files.list({
			q: `name='${fileName}' and '${targetFolderId}' in parents and trashed=false`,
			fields: 'files(id, name, size, modifiedTime, md5Checksum, version)',
		});

		console.log(`Found ${searchResponse.data.files.length} existing files`);

		if (searchResponse.data.files.length > 0) {
			const existingFile = searchResponse.data.files[0];
			console.log(`Existing file details:`, JSON.stringify(existingFile, null, 2));

			// Delete existing file
			console.log(`Deleting existing file with ID: ${existingFile.id}`);
			await drive.files.delete({ fileId: existingFile.id });
			console.log(`Existing file deleted successfully`);
		} else {
			console.log(`No existing file found`);
		}

		// Upload new file
		console.log(`Uploading new file to folder ID: ${targetFolderId}...`);
		const fileMetadata = {
			name: fileName,
			parents: [targetFolderId],
		};
		const media = {
			mimeType: 'application/pdf',
			body: fs.createReadStream(filePath),
		};

		const uploadResponse = await drive.files.create({
			resource: fileMetadata,
			media: media,
			fields: 'id, name, size, modifiedTime, md5Checksum, version, webViewLink',
		});

		console.log(`Upload successful!`);
		console.log(`New file details:`, JSON.stringify(uploadResponse.data, null, 2));

		// Verify the upload by getting file metadata
		console.log(`Verifying upload...`);
		const verifyResponse = await drive.files.get({
			fileId: uploadResponse.data.id,
			fields: 'id, name, size, modifiedTime, md5Checksum, version, webViewLink',
		});

		console.log(`Verification successful:`, JSON.stringify(verifyResponse.data, null, 2));

		return uploadResponse.data.id;
	} catch (error) {
		console.error(`Upload failed for ${fileName}:`, error);
		if (error.response) {
			console.error(`API Response:`, JSON.stringify(error.response.data, null, 2));
		}
		throw error;
	}
}

const downloadAndUpdatePDFs = async () => {
	console.log(`\n🚀 STARTING PDF DEBUG PROCESS`);
	console.log(`=================================`);
	console.log(`Process ID: ${process.pid}`);
	console.log(`Node version: ${process.version}`);
	console.log(`Working directory: ${process.cwd()}`);
	console.log(`Timestamp: ${new Date().toISOString()}`);
	console.log(`Environment: ${process.env.NODE_ENV || 'development'}`);

	// Log environment variables (safely)
	console.log(`\n=== ENVIRONMENT CHECK ===`);
	console.log(`GOOGLE_DRIVE_API_KEY: ${GOOGLE_DRIVE_API_KEY ? 'SET' : 'NOT SET'}`);
	console.log(`GOOGLE_DRIVE_ROOT_FOLDER_ID: ${GOOGLE_DRIVE_ROOT_FOLDER_ID || 'NOT SET'}`);
	console.log(`USER_NAME: ${USER_NAME}`);
	console.log(`USER_EMAIL: ${USER_EMAIL}`);
	console.log(`Target Drive Path: ${DRIVE_CONFIG.rootFolderId}/${DRIVE_CONFIG.targetPath}`);

	// Ensure the PDF_DIR exists
	console.log(`\n=== DIRECTORY SETUP ===`);
	if (!fs.existsSync(PDF_DIR)) {
		console.log(`PDF directory '${PDF_DIR}' does not exist. Creating it...`);
		fs.mkdirSync(PDF_DIR);
		console.log(`PDF directory '${PDF_DIR}' created successfully.`);
	} else {
		console.log(`PDF directory '${PDF_DIR}' already exists.`);
		// List existing files
		const existingFiles = fs.readdirSync(PDF_DIR);
		console.log(`Existing files in ${PDF_DIR}:`, existingFiles);
	}

	// Read package.json
	console.log(`\n=== PACKAGE INFO ===`);
	let packageName = 'default-package-name';
	try {
		const data = await fs.promises.readFile('./package.json', 'utf8');
		const packageJson = JSON.parse(data);
		packageName = packageJson.name;
		console.log(`Package name: ${packageName}`);
		console.log(`Package version: ${packageJson.version}`);
	} catch (err) {
		console.warn('Warning: Error reading package.json. Using default package name.', err.message);
	}

	// Initialize Google Drive
	let drive;
	try {
		drive = await setupGoogleDrive();
	} catch (error) {
		console.error('Google Drive setup failed. Aborting PDF update process.');
		console.error(error);
		process.exit(1);
	}

	// Process each URL
	console.log(`\n=== PROCESSING URLs ===`);
	console.log(`URLs to process: ${URLS.length}`);

	for (let i = 0; i < URLS.length; i++) {
		console.log(`\n--- Processing URL ${i + 1}/${URLS.length} ---`);

		const url = URLS[i];
		let fmtName = packageName[0].toUpperCase() + packageName.slice(1);
		fmtName = fmtName.replace('sf', 's-F');
		const filename = `${fmtName}${i === 0 ? '-en' : '-es'}.pdf`;
		const filePath = `${PDF_DIR}/${filename}`;

		console.log(`URL: ${url}`);
		console.log(`Filename: ${filename}`);
		console.log(`File path: ${filePath}`);

		try {
			await downloadPDF(url, filePath);
			const uploadId = await uploadToDrive(drive, filePath, filename);
			console.log(`✅ Successfully processed ${filename} (Drive ID: ${uploadId})`);
		} catch (err) {
			console.error(`❌ Error processing PDF from URL ${url}:`, err);
			console.error('Aborting PDF update process due to errors.');
			process.exit(1);
		}
	}

	console.log(`\n=== GIT OPERATIONS ===`);
	console.log('Configuring git user...');
	execSync(`git config --global user.name '${USER_NAME}'`);
	execSync(`git config --global user.email '${USER_EMAIL}'`);
	console.log('Git user configured.');

	console.log('Checking for changes before commit...');
	const statusOutput = execSync('git status --porcelain').toString();
	console.log(`Git status output:`, statusOutput);

	if (statusOutput) {
		const commitMessage = `📄 PDF Update [${new Date().toISOString()}] - Successfully updated resume files and backed up to Google Drive`;
		console.log('Changes detected. Adding, committing and pushing...');

		// Show what will be added
		const diffOutput = execSync('git diff --name-only').toString();
		console.log(`Files to be committed:`, diffOutput);

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

	console.log(`\n🎉 PDF DEBUG PROCESS COMPLETED`);
	console.log(`================================`);
	console.log(`Completion time: ${new Date().toISOString()}`);
};

// Handle unhandled rejections
process.on('unhandledRejection', (reason, promise) => {
	console.error('Unhandled Rejection at:', promise, 'reason:', reason);
	process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
	console.error('Uncaught Exception:', error);
	process.exit(1);
});

downloadAndUpdatePDFs();
