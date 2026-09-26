// Uses the user's installed ZCode CLI. ZCode itself is not redistributed.
const fs = require('node:fs');
const [prompt, cwd, session] = process.argv.slice(2);
const cli = process.env.ZCODE_CLI;
if (!cli || !prompt || !cwd) throw new Error('Set ZCODE_CLI and supply prompt-file project-dir [session-id]');
process.argv = [process.execPath, cli, '--prompt', fs.readFileSync(prompt, 'utf8'), '--cwd', cwd,
  '--json', '--mode', 'yolo', '--surface', 'terminal', ...(session ? ['--resume', session] : [])];
require(cli);
