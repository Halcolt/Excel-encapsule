# Excel Technical Debt Review

File tam de duyet cac hang muc dang do. Notion tam thoi de lai sau.

## Checklist De Xem Xet

- [x] CSRF tokens cho form/API POST
  - Danh gia: Nen lam som. App co upload/export qua POST, hien chua co token chong request gia mao.
  - Rui ro neu bo qua: Thap khi chi chay local, tang len neu expose trong LAN/internet.
  - De xuat: Them CSRF nhe bang session token va validate cho tat ca POST.

- [x] CSV encoding/delimiter detection
  - Danh gia: Nen lam som vi anh huong truc tiep den file thuc te cua nguoi dung.
  - Rui ro neu bo qua: File CSV tieng Viet hoac delimiter `;` co the doc sai cot/loi encoding.
  - De xuat: Thu cac encoding pho bien va dung `csv.Sniffer` de do delimiter.

- [x] Ban dich tieng Viet that cho giao dien
  - Danh gia: Nen lam som. Hien co nut ENG/VIE nhung `vi.json` van la tieng Anh.
  - Rui ro neu bo qua: Tinh nang i18n tao cam giac chua hoan thien.
  - De xuat: Dich cac chuoi UI hien co trong `vi.json`.

- [ ] App factory + Blueprints
  - Danh gia: Nen lam sau khi tinh nang on dinh. Hien `main.py` dang don khoang lon logic route/config/helper.
  - Rui ro neu bo qua: Kho test va kho tach module khi app lon hon.
  - De xuat: Refactor sau CSRF/CSV/test de tranh thay doi lon khi chua co luoi an toan.

- [ ] Services/ports va adapters cho storage/parser/export
  - Danh gia: Nen lam sau app factory. Huu ich neu muon test doc file/export rieng.
  - Rui ro neu bo qua: Logic pandas, upload temp, export dang nam chung trong route.
  - De xuat: Tach parser/export thanh module rieng khi bat dau viet test.

- [ ] Basic route/unit tests
  - Danh gia: Nen lam tiep theo sau khi co Python/Docker test environment san sang.
  - Rui ro neu bo qua: De hoi quy cac luong upload/select/render/export.
  - De xuat: Them pytest cho `_sanitize_sheet_name`, CSV detect, export shape va smoke test route.

- [ ] Drag-drop upload
  - Danh gia: Nice-to-have. UI hien da co file staging va add/remove file.
  - Rui ro neu bo qua: Khong anh huong chuc nang loi.
  - De xuat: Lam sau khi cac van de an toan/doc file duoc xu ly.

- [ ] MIME validation
  - Danh gia: Nen lam neu app duoc expose ngoai local.
  - Rui ro neu bo qua: Hien chi check extension, co the upload file khong dung dinh dang.
  - De xuat: Ket hop magic header validation cho `.xlsx` zip va CSV text.

- [ ] Persist edits/filters server-side
  - Danh gia: Lam sau. Hien moi thay doi nam tren browser cho den khi export.
  - Rui ro neu bo qua: Reload trang se mat edit/filter.
  - De xuat: Dung signed JSON/temporary storage neu can workflow dai hon.

- [ ] Cleanup docs/encoding mojibake
  - Danh gia: Nen lam rieng. Nhieu Markdown co ky tu bi loi nhu `â€‘`, `â†’`.
  - Rui ro neu bo qua: Doc kho chiu, nhung khong anh huong runtime.
  - De xuat: Sua encoding/noi dung docs sau khi chot huong phat trien.

- [ ] Cleanup file tam `temp_full.txt`, `temp_view.txt`, `helper_functions.txt`
  - Danh gia: Can xac nhan truoc khi xoa. Co ve la dump/template helper cu.
  - Rui ro neu bo qua: Repo roi, kho biet source of truth.
  - De xuat: Doi chieu voi template hien tai, sau do xoa hoac dua vao docs neu con gia tri.

## Uu Tien De Xuat

1. CSRF cho POST.
2. CSV encoding/delimiter detection.
3. Dich `vi.json`.
4. Them test khi co Python/Docker test command chay duoc.
5. Refactor app factory/Blueprints/services.
