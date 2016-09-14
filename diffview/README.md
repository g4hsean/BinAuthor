# Structure

- `static.html`: self-contained and static html
- `server.py`: Flask-based simple web server. It uses `templ.html` and `diffview.min.js`
- `templ.html`: Template for the web server
- `diffview.min.js`: JS client-side for the diffview
- `samples`: contains two simple ASM files

# Using the Flask-based appp

1. Launch the server `python server.py [--  port XXXX]` which by default will listen at 5000
2. Set WebView to URL `http://localhost:5000/diffview?left=samples/zlib.txt&right=samples/libpng.txt`.
Replace the left and right arguments by the files you want to display diff view.

# Using static html

You need to figure out to pass the data via Web View to the initialized script.

```js
//PASS THE DATA THROUGH WEBVIEW
(function _main_() {
var left = [
  'push edi',
  'mov dword ptr [eax+28h],0',
  'mov dword ptr [eax+2Ch],0',
  'mov dword ptr [eax+30h],0',
  'call inflateResetKeep',
  'add esp,4', 'pop esi',
  'pop edi',
  'pop ebx',
  'pop ebp',
  'retn'
];
var right = [
  'push eax',
  'mov [edi+8],ebx',
  'mov [edi+24h],esi',
  'call _inflateReset',
  'add esp,4',
  'pop esi',
  'pop ebx',
  'pop edi',
  'pop ebp',
  'retn' ];
displayDiffView(left, right);
})();
```

