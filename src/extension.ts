// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as path from 'path';

// Import the language client, language client options and server options from VSCode language client.
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient/node';

let client: LanguageClient;

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export async function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "nlp-bridge" is now active!');

	// finding out python
	const { python3 } = process.env;
	console.log(`Using python3 : ${python3}`);

	// if python3 is available continue
	if (python3) {
		// python3 execution path.
		let excecutable: string = python3;

		// path to the server.py
		let serverPath = path.join(__dirname, '..', '..', 'server', 'src', 'server.py');
		console.log('Executing ', serverPath);
		const args: string[] = [serverPath];

		// Set the server options 
		// -- java execution path
		// -- argument to be pass when executing the java command
		let serverOptions: ServerOptions = {
			command: excecutable,
			args: [...args],
			options: {}
		};

		// Options to control the language client
		let clientOptions: LanguageClientOptions = {
			// Register the server for plain text documents
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
}

// This method is called when your extension is deactivated
export function deactivate() {
	console.log('Extension was deactivated');
}

