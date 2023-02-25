// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as path from 'path';

// Import the language client, language client options and server options from VSCode language client.
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';
import { once } from 'events';

import * as fs from 'fs';
import * as readline from 'readline';
import {spawn} from 'child_process';

let client: LanguageClient;

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export async function activate(context: vscode.ExtensionContext) {

	let foundPython = false;

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "nlp-bridge" is now active!');

	let py = spawn('python3', ['-c', "print('Hello World')"]);

	// handle no-error output
	py.stdout.on('data', () => {
		console.log("Found python installation.");
		foundPython = true;

		vscode.window.showInformationMessage("Found python3");
	});

	// Handle error output
	py.stderr.on('data', (data: string) => {
		console.log("Error: ", data);
		foundPython = false;

		vscode.window.showErrorMessage("Couldn't find python3");
	});

	await once(py, 'close');

	// if python3 is available continue
	if (foundPython) {
		// path to the server directory
		let serverDirPath = path.join(__dirname, '..', 'server');

		// python3 executable path.
		let excecutable: string = path.join(serverDirPath, 'bin', 'python').toString();

		// create_venv.py path
		let createVenvScriptPath = path.join(serverDirPath, 'src', 'nlpserver', 'create_venv.py');
		console.log(`Creating virtual environment at ${serverDirPath}, if not created already`);
		spawn('python3', [createVenvScriptPath]);
		
		let requirementsPath = path.join(serverDirPath, 'requirements.txt');

		// logging the installation
		console.log("Installing dependencies");

		let r = readline.createInterface({
			input : fs.createReadStream(requirementsPath)
		});

		r.on('line', function (text: string) {
			console.log(text);
		});

		// installing dependencies if not present
		spawn(excecutable, ['-m', 'pip', '-r', requirementsPath]);

		// path to the server.py
		let serverScriptPath = path.join(serverDirPath, 'src', 'nlpserver', 'server.py');
		const args: string[] = [serverScriptPath];

		console.log('Executing ', serverScriptPath);

		// Set the server options 
		// python executable path
		// arguments
		let serverOptions: ServerOptions = {
			command: excecutable,
			args: [...args],
			options: {}
		};

		// Options to control the language client
		let clientOptions: LanguageClientOptions = {
			// Register the server for python documents
			documentSelector: [{ scheme: 'file', language: 'python' }]
		};

		client = new LanguageClient(
			'nlp-bridge',
			'nlp_bridge',
			serverOptions,
			clientOptions
		);

		await client.start();
	}

	context.subscriptions.push(vscode.commands.registerCommand('nlp-bridge.helloWorld', () => {
		vscode.window.showInformationMessage("Hello World");
	})
	);

}

export function deactivate(): Thenable<void> | undefined {
	console.log('Extension was deactivated');
	if (!client) {
		return undefined;
	}
		
	return client.stop();
}