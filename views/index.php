<?php
session_start();


if (!isset($_SESSION['username'])) {
    header('Location: login.php');
    exit;
}

// Aktifkan error reporting untuk debugging
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Koneksi ke database MySQL
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "attendance_system";

$conn = new mysqli($servername, $username, $password, $dbname);

// Periksa koneksi
if ($conn->connect_error) {
    die("Koneksi gagal: " . $conn->connect_error);
}

// Handle form submission
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (isset($_POST['take_attendance'])) {
        // Dapatkan path absolut script Python
        $pythonScript = 'c:/xampp/htdocs/absensi-wajah/test.py';
        
        // Dapatkan direktori script
        $scriptDir = dirname($pythonScript);
        
        // Konfigurasi descriptor untuk menangkap output
        $descriptorspec = [
           0 => ["pipe", "r"],  // stdin
           1 => ["pipe", "w"],  // stdout
           2 => ["pipe", "w"]   // stderr
        ];
        
        // Buka proses
        $process = proc_open(
            "python \"$pythonScript\"", 
            $descriptorspec, 
            $pipes, 
            $scriptDir // Set working directory
        );
        
        if (is_resource($process)) {
            // Baca output
            $stdout = stream_get_contents($pipes[1]);
            $stderr = stream_get_contents($pipes[2]);
            
            // Tutup pipe
            fclose($pipes[0]);
            fclose($pipes[1]);
            fclose($pipes[2]);
            
            // Dapatkan status
            $return_value = proc_close($process);
            
            // Log output untuk debugging
            error_log("Python Script Output (STDOUT): " . $stdout);
            error_log("Python Script Output (STDERR): " . $stderr);
            error_log("Return Value: " . $return_value);
            
            // Redirect dengan parameter sukses jika tidak ada error
            if ($return_value === 0) {
                header("Location: " . $_SERVER['PHP_SELF']);
            } else {
                header("Location: " . $_SERVER['PHP_SELF']);
            }
            exit();
        } else {
            // Gagal membuka proses
            error_log("Gagal membuka proses Python");
            header("Location: " . $_SERVER['PHP_SELF']);
            exit();
        }
    }
}

// Query untuk mengambil data kehadiran
$sql = "SELECT name, date, time, status FROM attendance ORDER BY date DESC, time DESC";
$result = $conn->query($sql);
?>

<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="../css/style.css">
    <title>Attendance Records</title>
</head>
<body>
    <h1 style="text-align: center;">Attendance Records</h1>

    <!-- Form untuk absensi -->
    <form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>">
        <input type="submit" name="take_attendance" value="Take Attendance" class="attendance-btn">
    </form>
    
    <table>
        <tr>
            <th>Name</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
        </tr>
        <?php
        if ($result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                $statusClass = ($row["status"] == "Active") ? "active" : "inactive";
                echo "<tr class='$statusClass'><td>" . $row["name"] . "</td><td>" . $row["date"] . "</td><td>" . $row["time"] . "</td><td>" . $row["status"] . "</td></tr>";
            }
        } else {
            echo "<tr><td colspan='4'>No records found</td></tr>";
        }
        ?>
    </table>

</body>
</html>

<?php
$conn->close();
?>