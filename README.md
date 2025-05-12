# Hệ Thống Quản Lý Bán Hàng Nội Thất

Hệ thống quản lý bán hàng nội thất toàn diện, tích hợp các tính năng từ nhiều dự án khác nhau, tạo ra một giải pháp hoàn chỉnh cho việc quản lý cửa hàng nội thất từ quy mô nhỏ đến lớn.

## Mục lục
- [Tổng quan hệ thống](#tổng-quan-hệ-thống)
- [Tính năng chính](#tính-năng-chính)
- [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
  - [Hướng dẫn cho Chủ doanh nghiệp](#hướng-dẫn-cho-chủ-doanh-nghiệp)
  - [Hướng dẫn cho Quản lý chi nhánh](#hướng-dẫn-cho-quản-lý-chi-nhánh)
  - [Hướng dẫn cho Nhân viên bán hàng](#hướng-dẫn-cho-nhân-viên-bán-hàng)
  - [Hướng dẫn cho Nhân viên kho](#hướng-dẫn-cho-nhân-viên-kho)
  - [Hướng dẫn cho Khách hàng](#hướng-dẫn-cho-khách-hàng)
- [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
- [Cài đặt](#cài-đặt)
- [Phát triển](#phát-triển)
- [Tính năng bảo mật](#tính-năng-bảo-mật)
- [Liên hệ và hỗ trợ](#liên-hệ-và-hỗ-trợ)

## Tổng quan hệ thống

Hệ thống Quản lý Bán hàng Nội thất cung cấp một nền tảng toàn diện để quản lý hoạt động kinh doanh nội thất. Hệ thống xử lý mọi khía cạnh từ quản lý kho hàng và sản phẩm đến xử lý bán hàng, quản lý nhân viên và báo cáo thống kê.

## Tính năng chính

### Quản lý người dùng và phân quyền
- Phân chia quyền hạn theo vai trò: Chủ doanh nghiệp, Quản lý chi nhánh, Nhân viên bán hàng, Nhân viên kho
- Xác thực đa yếu tố (2FA) tăng cường bảo mật
- Hệ thống phân quyền chi tiết với giao diện quản lý động

### Quản lý sản phẩm
- Hệ thống quản lý danh mục đa cấp
- Quản lý biến thể sản phẩm (màu sắc, kích thước, vật liệu...)
- Tìm kiếm và lọc sản phẩm nâng cao
- Tích hợp mã QR cho từng sản phẩm

### Quản lý kho hàng
- Theo dõi tồn kho theo thời gian thực
- Nhập và xuất kho với ghi chép đầy đủ
- Cảnh báo hết hàng và sắp hết hàng
- Chuyển kho giữa các chi nhánh
- Dự báo nhu cầu hàng hóa

### Quản lý đơn hàng
- Tạo và xử lý đơn hàng với quy trình linh hoạt
- Tích hợp nhiều phương thức thanh toán
- Theo dõi trạng thái đơn hàng
- In hóa đơn và phiếu giao hàng
- Quản lý trả hàng và hoàn tiền

### Quản lý chi nhánh
- Theo dõi hoạt động từng chi nhánh
- Báo cáo hiệu suất chi nhánh
- Quản lý nhân viên theo chi nhánh

### Quản lý nhà cung cấp
- Thông tin nhà cung cấp
- Lịch sử mua hàng
- Đánh giá nhà cung cấp

### Báo cáo và thống kê
- Báo cáo doanh thu với biểu đồ trực quan
- Báo cáo tồn kho
- Phân tích xu hướng bán hàng
- Xuất báo cáo đa định dạng: PDF, Excel, CSV
- Lên lịch gửi báo cáo tự động qua email

### Giao diện người dùng
- Thiết kế responsive hoàn toàn, hiển thị tối ưu trên mọi thiết bị
- Giao diện Material Design với hiệu ứng mượt mà
- Dark mode và Light mode linh hoạt
- Dashboard tùy chỉnh theo vai trò người dùng

## Hướng dẫn sử dụng

### Hướng dẫn cho Chủ doanh nghiệp

#### Đăng nhập và Trang chủ
1. **Đăng nhập hệ thống**
   - Truy cập vào hệ thống tại địa chỉ `http://[tên-miền]/admin/`
   - Nhập tài khoản và mật khẩu đã được cung cấp
   - Nếu đã kích hoạt 2FA, nhập mã xác thực từ ứng dụng bảo mật

2. **Dashboard chính**
   - Sau khi đăng nhập, bạn sẽ thấy dashboard tổng quan với các chỉ số kinh doanh quan trọng:
     - Tổng doanh số (ngày, tháng, năm)
     - Giá trị tồn kho
     - So sánh hiệu suất chi nhánh
     - Đơn hàng đang chờ xử lý

#### Quản lý người dùng và phân quyền
1. **Xem danh sách người dùng**
   - Truy cập: Accounts -> Quản lý người dùng
   - Bạn sẽ thấy danh sách tất cả người dùng trong hệ thống

2. **Thêm người dùng mới**
   - Nhấn nút "Thêm người dùng" và điền thông tin cần thiết
   - Chọn vai trò phù hợp: Quản lý, Nhân viên bán hàng, Nhân viên kho
   - Phân quyền chi tiết theo nhu cầu

3. **Quản lý quyền truy cập**
   - Truy cập: Hệ thống -> Phân quyền
   - Tùy chỉnh quyền cho từng vai trò hoặc người dùng cụ thể

#### Quản lý chi nhánh
1. **Xem danh sách chi nhánh**
   - Truy cập: Chi nhánh -> Danh sách chi nhánh
   - Xem thông tin tổng quan về tất cả chi nhánh

2. **Thêm chi nhánh mới**
   - Nhấn "Thêm chi nhánh" và nhập thông tin địa điểm, liên hệ
   - Thiết lập người quản lý chi nhánh

3. **Điều chuyển kho giữa chi nhánh**
   - Truy cập: Kho -> Điều chuyển kho
   - Tạo phiếu điều chuyển giữa các chi nhánh

#### Báo cáo và phân tích
1. **Xem báo cáo doanh thu**
   - Truy cập: Báo cáo -> Dashboard
   - Chọn loại báo cáo: Doanh số, Tồn kho, Tài chính
   - Lọc theo thời gian: ngày, tuần, tháng, năm

2. **Xuất báo cáo**
   - Nhấn nút "Xuất báo cáo" để tải xuống dưới dạng PDF, Excel, CSV
   - Thiết lập lịch gửi báo cáo tự động qua email

### Hướng dẫn cho Quản lý chi nhánh

#### Quản lý chi nhánh
1. **Dashboard chi nhánh**
   - Đăng nhập tại `http://[tên-miền]/branch/`
   - Dashboard hiển thị các chỉ số chi nhánh:
     - Doanh số và mục tiêu hàng ngày
     - Hiệu suất nhân viên
     - Tồn kho hiện tại
     - Đơn hàng đang chờ xử lý

2. **Quản lý nhân viên**
   - Truy cập: Nhân viên -> Danh sách nhân viên
   - Thêm nhân viên mới: Nhấn "Thêm nhân viên" và hoàn thành biểu mẫu
   - Thiết lập lịch làm việc: Sử dụng tab "Lịch" trong chi tiết nhân viên
   - Theo dõi hiệu suất: Xem chỉ số hiệu suất cá nhân

3. **Quản lý kho hàng**
   - Truy cập: Kho -> Kho chi nhánh
   - Yêu cầu nhập kho: Sử dụng "Yêu cầu nhập kho" khi cần bổ sung hàng
   - Nhận hàng: Xử lý nhận hàng với "Nhận kho"
   - Kiểm kho: Bắt đầu kiểm kho với "Bắt đầu kiểm kho" và làm theo quy trình

4. **Giám sát bán hàng**
   - Truy cập: Bán hàng -> Bán hàng chi nhánh
   - Xem tất cả giao dịch: Lọc theo ngày, nhân viên hoặc sản phẩm
   - Xử lý khiếu nại: Xử lý trả hàng và đổi trả trong mục Bán hàng -> Trả hàng
   - Duyệt giảm giá đặc biệt: Xem yêu cầu giảm giá dưới mục Bán hàng -> Phê duyệt

#### Báo cáo chi nhánh
1. **Báo cáo hàng ngày**
   - Tạo báo cáo cuối ngày trong phần Báo cáo -> Hàng ngày
   - Kiểm tra và xác nhận doanh số trước khi đóng cửa

2. **Báo cáo nhân viên**
   - Xem chỉ số chi tiết trong Báo cáo -> Nhân viên
   - Đánh giá hiệu suất và thiết lập mục tiêu

3. **Báo cáo tồn kho**
   - Kiểm tra trạng thái kho trong Báo cáo -> Kho
   - Xác định sản phẩm cần nhập thêm hoặc khuyến mãi

### Hướng dẫn cho Nhân viên bán hàng

#### Hoạt động hàng ngày
1. **Hệ thống bán hàng (POS)**
   - Đăng nhập tại `http://[tên-miền]/pos/`
   - Tạo đơn hàng mới: Nhấn nút "Tạo đơn hàng"
   - Thêm sản phẩm: Quét mã vạch hoặc tìm kiếm tên sản phẩm
   - Áp dụng giảm giá: Sử dụng nút giảm giá nếu được phép
   - Xử lý thanh toán: Chọn phương thức thanh toán và hoàn tất giao dịch

2. **Quản lý khách hàng**
   - Thêm khách hàng mới: Nhấn "Thêm khách hàng" trong quá trình bán hàng
   - Tìm kiếm khách hàng: Sử dụng thanh tìm kiếm trong giao diện POS
   - Xem lịch sử mua hàng: Truy cập chi tiết khách hàng

3. **Thông tin sản phẩm**
   - Kiểm tra tồn kho: Sử dụng chức năng "Kiểm tra tồn kho" trong POS
   - Xem thông tin chi tiết: Truy cập toàn bộ thông tin với "Thông tin sản phẩm"
   - So sánh sản phẩm: Sử dụng tính năng "So sánh" để giới thiệu các lựa chọn thay thế

4. **Quản lý đơn hàng**
   - Tạo đơn đặt hàng: Sử dụng "Đơn đặt hàng" cho sản phẩm không có sẵn
   - Theo dõi đơn hàng: Xem trong mục Đơn hàng -> Theo dõi
   - Thông báo khách hàng: Gửi cập nhật qua hệ thống với "Thông báo khách hàng"

#### Dịch vụ khách hàng
1. **Xử lý trả hàng và đổi hàng**
   - Xử lý trả hàng: Chọn "Trả hàng" trong POS và quét hóa đơn gốc
   - Xử lý đổi hàng: Sử dụng tùy chọn "Đổi hàng" và làm theo quy trình
   - Phát hành tín dụng cửa hàng: Chọn "Tín dụng cửa hàng" làm tùy chọn hoàn tiền

2. **Phản hồi khách hàng**
   - Ghi lại phản hồi: Nhập nhận xét khách hàng trong mục Khách hàng -> Phản hồi
   - Xử lý khiếu nại: Ghi lại vấn đề và các bước giải quyết
   - Theo dõi: Lên lịch các hành động theo dõi với lời nhắc

3. **In hóa đơn và lưu trữ**
   - In hóa đơn sau mỗi giao dịch
   - Xem hóa đơn đã lưu: Truy cập hóa đơn bán hàng trong khoảng thời gian tùy chọn
   - Xem thống kê bán hàng theo ngày, tháng

4. **Duyệt và hủy đơn hàng**
   - Duyệt đơn hàng: Xác nhận đơn hàng của khách trong mục Đơn hàng
   - Hủy đơn hàng: Chọn tùy chọn hủy và ghi lại lý do

### Hướng dẫn cho Nhân viên kho

#### Quản lý kho hàng
1. **Nhận hàng**
   - Đăng nhập tại `http://[tên-miền]/inventory/`
   - Xử lý nhận hàng: Nhấn "Nhận hàng" và nhập số đơn đặt hàng
   - Kiểm tra chất lượng: Sử dụng "Kiểm tra chất lượng" để ghi lại tình trạng hàng nhận
   - Lưu kho: Cập nhật thông tin vị trí trong "Phân kho"

2. **Quản lý tồn kho**
   - Theo dõi tồn kho: Xem mức tồn kho hiện tại trong Kho -> Mức tồn kho
   - Di chuyển hàng: Cập nhật vị trí với "Di chuyển kho"
   - Đặt hàng: Đánh dấu mặt hàng đã đặt trước với "Đặt trước hàng"
   - Kiểm đếm: Thực hiện kiểm đếm kho định kỳ với "Kiểm kho"

3. **Thực hiện đơn hàng**
   - Xử lý đơn hàng: Xem đơn hàng đang chờ trong Đơn hàng -> Đang chờ
   - Chọn và đóng gói: Làm theo quy trình với "Chọn đơn hàng"
   - Chuẩn bị giao hàng: Tạo nhãn vận chuyển với "Chuẩn bị giao hàng"
   - Đánh dấu đã gửi: Cập nhật trạng thái với "Đánh dấu đã gửi"

4. **Chuyển kho**
   - Xử lý yêu cầu chuyển: Xem trong mục Chuyển kho -> Đang chờ
   - Chuẩn bị chuyển kho: Sử dụng quy trình "Chuẩn bị chuyển kho"
   - Nhận chuyển kho: Xử lý với "Nhận chuyển kho"
   - Theo dõi trạng thái: Giám sát trong Chuyển kho -> Đang hoạt động

5. **Quản lý sản phẩm**
   - Thêm, sửa, xóa sản phẩm trong kho
   - Thêm, sửa, xóa thông tin nhà cung cấp
   - Tìm kiếm và sắp xếp theo sản phẩm, nhà cung cấp
   - Lập phiếu nhập kho và in, lưu trữ phiếu

#### Bảo trì
1. **Thiết bị và cơ sở vật chất**
   - Báo cáo vấn đề: Ghi lại sự cố cơ sở vật chất trong Bảo trì -> Báo cáo
   - Theo dõi sửa chữa: Giám sát trạng thái yêu cầu bảo trì
   - Lên lịch bảo trì: Thiết lập kiểm tra thường xuyên trong Bảo trì -> Lịch

2. **Tài liệu**
   - Hồ sơ vận chuyển: Truy cập trong Tài liệu -> Vận chuyển
   - Hồ sơ nhận hàng: Xem trong Tài liệu -> Nhận hàng
   - Nhật ký chuyển kho: Xem lịch sử đầy đủ trong Tài liệu -> Chuyển kho

### Hướng dẫn cho Khách hàng

#### Duyệt và mua sắm
1. **Duyệt sản phẩm**
   - Xem thông tin sản phẩm và tình trạng tồn kho
   - Tìm kiếm sản phẩm theo tên, danh mục
   - Lọc theo giá, thương hiệu, tính năng

2. **Quy trình mua hàng**
   - Thêm sản phẩm vào giỏ hàng
   - Xem và chỉnh sửa giỏ hàng
   - Tiến hành thanh toán
   - Chọn phương thức thanh toán và giao hàng

3. **Theo dõi đơn hàng**
   - Đăng nhập vào tài khoản khách hàng
   - Xem trạng thái đơn hàng hiện tại
   - Kiểm tra lịch sử đơn hàng

4. **Trả hàng và hoàn tiền**
   - Yêu cầu trả hàng trong tài khoản khách hàng
   - In nhãn trả hàng
   - Theo dõi quá trình hoàn tiền

## Cấu trúc dự án

```
FurnitureSystem/
│
├── apps/                   # Thư mục chứa các ứng dụng Django
│   ├── accounts/           # Quản lý người dùng và phân quyền
│   ├── branches/           # Quản lý chi nhánh
│   ├── cart/               # Giỏ hàng và xử lý mua sắm
│   ├── inventory/          # Quản lý kho hàng và tồn kho
│   ├── orders/             # Quản lý đơn hàng và thanh toán
│   ├── products/           # Quản lý sản phẩm và danh mục
│   ├── reports/            # Báo cáo và thống kê
│   ├── staff/              # Giao diện dành cho nhân viên
│   └── suppliers/          # Quản lý nhà cung cấp
├── core/                   # Cấu hình dự án Django chính
├── media/                  # Lưu trữ file người dùng tải lên
│   ├── categories/         # Hình ảnh danh mục
│   ├── products/           # Hình ảnh sản phẩm
│   └── user_uploads/       # Các file người dùng tải lên khác
├── static/                 # File tĩnh (CSS, JS, hình ảnh)
│   ├── css/
│   ├── img/
│   └── js/
├── templates/              # HTML templates
│   ├── accounts/
│   ├── base/
│   ├── branches/
│   ├── cart/
│   ├── home/
│   ├── orders/
│   ├── products/
│   └── staff/
├── utils/                  # Các tiện ích và hàm hỗ trợ
├── manage.py               # Script quản lý Django
└── requirements.txt        # Danh sách thư viện phụ thuộc
```

## Yêu cầu hệ thống

- Python 3.10+
- Django 5.2
- Cơ sở dữ liệu: SQLite (phát triển), PostgreSQL (sản xuất)
- Các thư viện phụ thuộc được liệt kê trong `requirements.txt`

## Cài đặt

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd FurnitureSystem
   ```

2. **Tạo môi trường ảo**
   ```bash
   python -m venv .venv
   ```

3. **Kích hoạt môi trường ảo**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Cài đặt các gói phụ thuộc**
   ```bash
   pip install -r requirements.txt
   ```

5. **Thực hiện migration**
   ```bash
   python manage.py migrate
   ```

6. **Tạo tài khoản admin**
   ```bash
   python manage.py createsuperuser
   ```

7. **Chạy server phát triển**
   ```bash
   python manage.py runserver
   ```

8. **Truy cập hệ thống**
   - Trang admin: http://localhost:8000/admin/
   - Trang chủ: http://localhost:8000/

## Phát triển

- Cài đặt thêm các dependency cho môi trường phát triển
  ```bash
  pip install -r requirements-dev.txt
  ```
- Chạy kiểm thử
  ```bash
  python manage.py test
  ```

## Tính năng bảo mật

- Xác thực đa yếu tố (2FA)
- CSRF và XSS protection
- Rate limiting
- Audit logging cho mọi hoạt động
- Mã hóa dữ liệu nhạy cảm
- HTTPS bắt buộc

## Liên hệ và hỗ trợ

- **Email**: support@noithat.com
- **Điện thoại**: 0123 456 789
- **Website**: https://noithat.com 