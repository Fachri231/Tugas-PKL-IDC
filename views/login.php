<?php 
session_start();

$conn = mysqli_connect('localhost', 'root', '', 'attendance_system');

$users = mysqli_query($conn, "SELECT * FROM users");
$users = mysqli_fetch_assoc($users);

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if($users['username'] == $_POST['username'] && $users['password'] == $_POST['password']) {
        $_SESSION['username'] = $users['username'];
        header('Location: index.php');
    } else {
        echo 'Paaword Atau Username Salah';
    }
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form Login</title>
    <link rel="stylesheet" href="../css/login.css">
</head>
<body>
    <div class="container">
    <h1>Login</h1>

    <form action="" method="post">
        <div class="input">
            <label for="username">Username :</label>
            <input type="text" name="username" required>
        </div>
        <div class="input">
            <label for="password">Password :</label>
            <input type="password" name="password" required>
        </div>
        <button type="submit" name="login">Login</button>
    </form>
    </div>
</body>
</html>