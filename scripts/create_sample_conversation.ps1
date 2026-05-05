$ErrorActionPreference = "Stop"

function Decode-Utf8Base64([string]$value) {
    [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($value))
}

$inputDir = Join-Path (Resolve-Path ".").Path "data\input"
New-Item -ItemType Directory -Force -Path $inputDir | Out-Null

$wavPath = Join-Path $inputDir "sample_family_conversation.wav"
$m4aPath = Join-Path $inputDir "sample_family_conversation.m4a"
$transcriptPath = Join-Path $inputDir "sample_family_conversation_reference.md"

foreach ($path in @($wavPath, $m4aPath, $transcriptPath)) {
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Force
    }
}

$voice = New-Object -ComObject SAPI.SpVoice
$stream = New-Object -ComObject SAPI.SpFileStream
$stream.Open($wavPath, 3, $false)
$voice.AudioOutputStream = $stream

$voices = @{}
$voice.GetVoices() | ForEach-Object {
    $description = $_.GetDescription()
    if ($description -like "*David*") { $voices["David"] = $_ }
    if ($description -like "*Zira*") { $voices["Zira"] = $_ }
}

$moshe = Decode-Utf8Base64 "157XqdeU"
$david = Decode-Utf8Base64 "15PXldeZ15M="

$conversation = @(
    @{ Voice = "David"; Speaker = $moshe; Text = (Decode-Utf8Base64 "157XlCDXp9eV16jXlCDXk9eV15nXkz8="); AudioText = "Moshe: ma kore David?" },
    @{ Voice = "Zira"; Speaker = $david; Text = (Decode-Utf8Base64 "16LXlteV15Eg15DXldeq15kuINeQ15nXnyDXnNeZINeb15cg15DXnNeZ15ou"); AudioText = "David: azov oti. ein li koach eleicha." },
    @{ Voice = "David"; Speaker = $moshe; Text = (Decode-Utf8Base64 "15HXkCDXnNeaINec15zXm9eqINec16TXkNeo16c/"); AudioText = "Moshe: ba lecha lalechet la park?" },
    @{ Voice = "Zira"; Speaker = $david; Text = (Decode-Utf8Base64 "15DXoNeZINeQ15fXqdeV15Eg16LXnCDXlteULiDXkNeg15kg16jXldem15Qg15zXoNeV15cu"); AudioText = "David: ani echshov al ze. ani rotze lanuach." },
    @{ Voice = "David"; Speaker = $moshe; Text = (Decode-Utf8Base64 "15TXm9eg16rXmSDXkNeo15XXl9eqINeR15XXp9eoLg=="); AudioText = "Moshe: hechnati aruchat boker." },
    @{ Voice = "Zira"; Speaker = $david; Text = (Decode-Utf8Base64 "16rXldeT15Qu"); AudioText = "David: toda." }
)

foreach ($turn in $conversation) {
    if ($voices.ContainsKey($turn.Voice)) {
        $voice.Voice = $voices[$turn.Voice]
    }
    [void]$voice.Speak($turn.AudioText)
    [void]$voice.Speak(" ")
}

$stream.Close()

$referenceLines = @(
    "# Sample Family Conversation Reference",
    "",
    "This file contains the Hebrew dialogue requested by the user.",
    "The local machine currently exposes only English Windows voices, so the synthetic Hebrew pronunciation may sound unnatural.",
    "",
    ("1. " + $conversation[0].Speaker + ": " + $conversation[0].Text),
    ("2. " + $conversation[1].Speaker + ": " + $conversation[1].Text),
    ("3. " + $conversation[2].Speaker + ": " + $conversation[2].Text),
    ("4. " + $conversation[3].Speaker + ": " + $conversation[3].Text),
    ("5. " + $conversation[4].Speaker + ": " + $conversation[4].Text),
    ("6. " + $conversation[5].Speaker + ": " + $conversation[5].Text),
    "",
    "For real Hebrew transcription quality checks, use a real Hebrew recording."
)
[IO.File]::WriteAllLines($transcriptPath, $referenceLines, [Text.UTF8Encoding]::new($false))

$python = @"
from pathlib import Path
import subprocess
import imageio_ffmpeg

wav_path = Path(r"$wavPath")
m4a_path = Path(r"$m4aPath")
command = [
    imageio_ffmpeg.get_ffmpeg_exe(),
    "-y",
    "-i",
    str(wav_path),
    "-c:a",
    "aac",
    "-b:a",
    "96k",
    str(m4a_path),
]
completed = subprocess.run(command, capture_output=True, text=True, check=False)
if completed.returncode:
    raise SystemExit(completed.stderr)
print(m4a_path)
"@

$python | uv run --with imageio-ffmpeg python -
Write-Output $transcriptPath
