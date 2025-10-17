
/**
 * A列の2行目以降に 1,2,3,... と連番を振る
 * （今ある最終行まで自動で）
 */
function fillNumbersInAColumn() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastRow = sheet.getLastRow();

  if (lastRow < 2) {
    SpreadsheetApp.getUi().alert("2行目以降にデータがありません。");
    return;
  }

  var numbers = [];
  for (var i = 2; i <= lastRow; i++) {
    numbers.push([i - 1]);
  }

  // A列に一括で書き込み
  sheet.getRange(2, 1, numbers.length, 1).setValues(numbers);

  // 折り返し設定OFF（見た目調整）
  sheet.getRange(2, 1, numbers.length, 1).setWrap(false);
}
