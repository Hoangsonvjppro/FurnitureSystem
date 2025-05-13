# Hệ Thống Quản Lý Bán Hàng Nội Thất

Hệ thống quản lý bán hàng nội thất toàn diện, tích hợp các tính năng từ nhiều dự án khác nhau, tạo ra một giải pháp hoàn chỉnh cho việc quản lý cửa hàng nội thất từ quy mô nhỏ đến lớn.

## Mục lục
- [Tổng quan hệ thống](#tổng-quan-hệ-thống)
- [Tính năng chính](#tính-năng-chính)
- [Hướng dẫn sử dụng đầu tiên](#hướng-dẫn-sử-dụng-đầu-tiên)
  - [Đăng nhập hệ thống](#đăng-nhập-hệ-thống)
  - [Thiết lập ban đầu](#thiết-lập-ban-đầu)
  - [Tạo và quản lý tài khoản](#tạo-và-quản-lý-tài-khoản)
  - [Phân quyền người dùng](#phân-quyền-người-dùng)
- [Hướng dẫn theo vai trò](#hướng-dẫn-theo-vai-trò)
  - [Hướng dẫn cho Admin](#hướng-dẫn-cho-admin)
  - [Hướng dẫn cho Quản lý chi nhánh](#hướng-dẫn-cho-quản-lý-chi-nhánh)
  - [Hướng dẫn cho Nhân viên bán hàng](#hướng-dẫn-cho-nhân-viên-bán-hàng)
  - [Hướng dẫn cho Nhân viên kho](#hướng-dẫn-cho-nhân-viên-kho)
  - [Hướng dẫn cho Khách hàng](#hướng-dẫn-cho-khách-hàng)
- [Cài đặt và triển khai](#cài-đặt-và-triển-khai)
- [Liên hệ và hỗ trợ](#liên-hệ-và-hỗ-trợ)

## Tổng quan hệ thống

Hệ thống Quản lý Bán hàng Nội thất cung cấp một nền tảng toàn diện để quản lý hoạt động kinh doanh nội thất. Hệ thống xử lý mọi khía cạnh từ quản lý kho hàng và sản phẩm đến xử lý bán hàng, quản lý nhân viên và báo cáo thống kê.

## Tính năng chính

### Quản lý người dùng và phân quyền
- Phân chia quyền hạn theo vai trò: Admin, Quản lý chi nhánh, Nhân viên bán hàng, Nhân viên kho
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

### Báo cáo và thống kê
- Báo cáo doanh thu với biểu đồ trực quan
- Báo cáo tồn kho
- Phân tích xu hướng bán hàng
- Xuất báo cáo đa định dạng: PDF, Excel, CSV

## Hướng dẫn sử dụng đầu tiên

### Đăng nhập hệ thống

Khi mới cài đặt hệ thống, bạn cần đăng nhập bằng tài khoản superuser đã tạo:

1. Truy cập vào URL: `http://domain-của-bạn/admin/`
2. Đăng nhập bằng tài khoản superuser (đã tạo bằng lệnh `python manage.py createsuperuser`)
3. Sau khi đăng nhập, bạn sẽ thấy trang quản trị Django với giao diện Jazzmin

### Thiết lập ban đầu

Trước khi bắt đầu sử dụng hệ thống, bạn cần thực hiện một số thiết lập ban đầu:

1. **Tạo chi nhánh**:
   - Trong admin, vào phần "Branches" > "Thêm Chi nhánh"
   - Nhập thông tin chi nhánh chính và các chi nhánh khác (nếu có)
   - Mỗi chi nhánh cần có tên, địa chỉ và số điện thoại

2. **Tạo danh mục sản phẩm**:
   - Vào phần "Products" > "Danh mục" > "Thêm Danh mục"
   - Tạo các danh mục sản phẩm chính và danh mục con (nếu cần)

3. **Tạo các sản phẩm**:
   - Vào phần "Products" > "Sản phẩm" > "Thêm Sản phẩm"
   - Mỗi sản phẩm cần có tên, mã sản phẩm (SKU), giá, danh mục và hình ảnh
   - Có thể thêm biến thể sản phẩm (màu sắc, kích thước, v.v.)

4. **Thiết lập kho ban đầu**:
   - Vào phần "Inventory" > "Kho" > "Thêm Kho"
   - Tạo kho hàng cho mỗi chi nhánh
   - Thêm hàng tồn kho cho các sản phẩm

### Tạo và quản lý tài khoản

#### Tạo tài khoản người dùng mới

1. **Đăng nhập với tài khoản Admin**
2. **Tạo tài khoản thông qua Admin panel**:
   - Vào phần "Accounts" > "Người dùng" > "Thêm Người dùng"
   - Nhập thông tin cơ bản: username, email, mật khẩu, họ tên
   - Lưu lại để tạo tài khoản

#### Cấu hình vai trò người dùng

Sau khi tạo tài khoản, bạn cần thiết lập vai trò cho người dùng:

1. **Tài khoản Quản lý chi nhánh**:
   - Chọn người dùng đã tạo
   - Đánh dấu tùy chọn "Quản lý chi nhánh" (is_branch_manager)
   - Chọn chi nhánh mà người này quản lý trong trường "Chi nhánh"
   - Tùy chọn có thể đánh dấu "Nhân viên" (is_staff) để cho phép truy cập trang admin

2. **Tài khoản Nhân viên bán hàng**:
   - Chọn người dùng đã tạo
   - Đánh dấu tùy chọn "Nhân viên bán hàng" (is_sales_staff)
   - Chọn chi nhánh làm việc trong trường "Chi nhánh"

3. **Tài khoản Nhân viên kho**:
   - Chọn người dùng đã tạo
   - Đánh dấu tùy chọn "Nhân viên kho" (is_inventory_staff)
   - Chọn chi nhánh làm việc trong trường "Chi nhánh"

4. **Tài khoản Khách hàng**:
   - Khách hàng có thể tự đăng ký thông qua trang đăng ký
   - Hoặc admin có thể tạo tài khoản khách hàng và thêm thông tin chi tiết trong "CustomerProfile"

### Phân quyền người dùng

Hệ thống sử dụng phân quyền dựa trên vai trò (role-based permissions):

1. **Vào phần quản lý quyền**:
   - Trong admin, vào phần "Authentication and Authorization" > "Groups"
   - Tạo các nhóm tương ứng với vai trò: Branch Managers, Sales Staff, Inventory Staff, Customers

2. **Thiết lập quyền cho từng nhóm**:
   - Chọn nhóm cần cấu hình
   - Thêm các quyền phù hợp với vai trò đó

3. **Thêm người dùng vào nhóm**:
   - Sau khi tạo nhóm, chọn người dùng
   - Trong phần "Groups", thêm người dùng vào nhóm tương ứng

## Hướng dẫn theo vai trò

### Hướng dẫn cho Admin

#### Quản lý hệ thống
1. **Quản lý người dùng**:
   - Tạo, chỉnh sửa hoặc vô hiệu hóa tài khoản người dùng
   - Phân quyền cho người dùng theo vai trò

2. **Quản lý chi nhánh**:
   - Tạo chi nhánh mới
   - Chỉ định quản lý cho chi nhánh
   - Xem báo cáo tổng hợp từ tất cả chi nhánh

3. **Cấu hình hệ thống**:
   - Cài đặt các tham số hệ thống
   - Cấu hình tích hợp email, thanh toán

4. **Truy cập báo cáo tổng quan**:
   - Xem báo cáo doanh thu toàn hệ thống
   - Phân tích hiệu suất theo chi nhánh và nhân viên

5. **Đánh giá nhân viên**:
   - Tạo các đánh giá định kỳ cho nhân viên
   - Đánh giá hiệu suất làm việc theo nhiều tiêu chí
   - Xuất phiếu đánh giá dưới dạng PDF
   - Theo dõi quá trình phát triển của nhân viên qua thời gian

### Hướng dẫn cho Quản lý chi nhánh

#### Quản lý chi nhánh
1. **Quản lý nhân viên chi nhánh**:
   - Xem danh sách nhân viên thuộc chi nhánh
   - Phân công công việc và quản lý lịch làm việc

2. **Xem báo cáo chi nhánh**:
   - Truy cập báo cáo doanh số chi nhánh
   - Theo dõi hiệu suất nhân viên

3. **Quản lý tồn kho chi nhánh**:
   - Xem tình trạng tồn kho
   - Yêu cầu nhập hàng khi cần thiết

4. **Xét duyệt đơn hàng**:
   - Xét duyệt các đơn hàng đặc biệt
   - Xử lý yêu cầu hoàn tiền và khiếu nại

### Hướng dẫn cho Nhân viên bán hàng

#### Tác vụ bán hàng
1. **Tạo đơn hàng mới**:
   - Từ menu, vào "Orders" > "Tạo đơn hàng"
   - Thêm sản phẩm vào đơn hàng từ danh sách sản phẩm
   - Nhập thông tin khách hàng hoặc chọn từ danh sách khách hàng có sẵn
   - Áp dụng giảm giá nếu có và hoàn tất đơn hàng

2. **Quản lý giỏ hàng khách**:
   - Thêm sản phẩm vào giỏ hàng khách
   - Cập nhật số lượng hoặc xóa sản phẩm
   - Chuyển từ giỏ hàng sang đơn hàng

3. **Xem thông tin sản phẩm**:
   - Kiểm tra thông tin chi tiết sản phẩm
   - Xem tồn kho hiện tại tại chi nhánh
   - Tìm kiếm sản phẩm theo tên, mã hoặc danh mục

4. **Xử lý thanh toán**:
   - Nhận thanh toán từ khách hàng
   - Ghi nhận phương thức thanh toán
   - In hóa đơn

5. **Quản lý đơn hàng**:
   - Duyệt đơn hàng của khách hàng
   - Cập nhật trạng thái đơn hàng (đang xử lý, đang giao, đã giao, đã hủy)
   - Hủy đơn hàng khi cần thiết và ghi chú lý do

6. **In và lưu trữ hóa đơn**:
   - Tạo và xuất hóa đơn bán hàng dưới dạng PDF
   - Lưu trữ hóa đơn trong hệ thống để tham khảo sau này
   - Gửi hóa đơn qua email cho khách hàng (nếu cần)

7. **Xem lịch sử đơn hàng**:
   - Tra cứu đơn hàng theo thời gian (ngày, tháng, năm)
   - Lọc đơn hàng theo trạng thái, phương thức thanh toán
   - Xem thống kê doanh số bán hàng cá nhân

### Hướng dẫn cho Nhân viên kho

#### Quản lý kho
1. **Nhận hàng**:
   - Tiếp nhận hàng từ nhà cung cấp
   - Kiểm tra và cập nhật tồn kho

2. **Kiểm kho**:
   - Thực hiện kiểm kho định kỳ
   - Ghi nhận sai lệch nếu có

3. **Chuyển kho**:
   - Thực hiện chuyển hàng giữa các chi nhánh
   - Xác nhận nhận/chuyển hàng

4. **Xuất hàng**:
   - Chuẩn bị hàng cho đơn hàng
   - Xác nhận xuất kho

### Hướng dẫn cho Khách hàng

#### Mua sắm trực tuyến
1. **Đăng ký/đăng nhập**:
   - Tạo tài khoản mới hoặc đăng nhập
   - Cập nhật thông tin cá nhân

2. **Duyệt sản phẩm**:
   - Xem danh sách sản phẩm theo danh mục
   - Tìm kiếm sản phẩm
   - Xem chi tiết sản phẩm

3. **Mua hàng**:
   - Thêm sản phẩm vào giỏ hàng
   - Tiến hành thanh toán
   - Chọn phương thức thanh toán và giao hàng

4. **Theo dõi đơn hàng**:
   - Xem lịch sử đơn hàng
   - Kiểm tra trạng thái đơn hàng hiện tại

## Cài đặt và triển khai

### Yêu cầu hệ thống
- Python 3.8+
- Django 3.2+
- PostgreSQL hoặc SQLite
- Các gói phụ thuộc trong requirements.txt

### Cài đặt
1. Clone repository
   ```bash
   git clone <repository-url>
   cd FurnitureSystem
   ```

2. Tạo môi trường ảo
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # hoặc
   .venv\Scripts\activate     # Windows
   ```

3. Cài đặt các gói phụ thuộc
   ```bash
   pip install -r requirements.txt
   ```

4. Thực hiện migration
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Tạo tài khoản superuser
   ```bash
   python manage.py createsuperuser
   ```

6. Khởi động server
   ```bash
   python manage.py runserver
   ```

## Liên hệ và hỗ trợ

- **Email**: support@noithat.com
- **Điện thoại**: 0123 456 789
- **Website**: https://noithat.com 