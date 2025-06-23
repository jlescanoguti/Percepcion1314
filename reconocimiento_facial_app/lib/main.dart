import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sistema de Reconocimiento Facial',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF6750A4),
          brightness: Brightness.light,
        ),
        appBarTheme: const AppBarTheme(
          centerTitle: true,
          elevation: 0,
          backgroundColor: Colors.transparent,
          foregroundColor: Colors.white,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            elevation: 8,
            shadowColor: Colors.black26,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          ),
        ),
        cardTheme: CardTheme(
          elevation: 8,
          shadowColor: Colors.black26,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
        ),
      ),
      home: LandingPage(),
    );
  }
}

class LandingPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF6750A4),
              Color(0xFF9C27B0),
              Color(0xFFE91E63),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header con título
              Container(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    const Icon(
                      Icons.face_retouching_natural,
                      size: 80,
                      color: Colors.white,
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Sistema de Reconocimiento Facial',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Gestión inteligente de usuarios',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.white.withOpacity(0.8),
                      ),
                    ),
                  ],
                ),
              ),
              
              // Menú de opciones
              Expanded(
                child: Container(
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(30),
                      topRight: Radius.circular(30),
                    ),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: GridView.count(
                      crossAxisCount: 2,
                      crossAxisSpacing: 16,
                      mainAxisSpacing: 16,
                      children: [
                        _buildMenuCard(
                          context,
                          'Registrar Usuario',
                          Icons.person_add,
                          Colors.blue,
                          () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegistrarUsuarioScreen())),
                        ),
                        _buildMenuCard(
                          context,
                          'Lista de Usuarios',
                          Icons.people,
                          Colors.green,
                          () => Navigator.push(context, MaterialPageRoute(builder: (_) => ListaUsuariosScreen())),
                        ),
                        _buildMenuCard(
                          context,
                          'Consultar Usuario',
                          Icons.search,
                          Colors.orange,
                          () => Navigator.push(context, MaterialPageRoute(builder: (_) => ConsultarUsuarioScreen())),
                        ),
                        _buildMenuCard(
                          context,
                          'Editar Usuario',
                          Icons.edit,
                          Colors.purple,
                          () => Navigator.push(context, MaterialPageRoute(builder: (_) => EditarUsuarioScreen())),
                        ),
                        _buildMenuCard(
                          context,
                          'Eliminar Usuario',
                          Icons.delete,
                          Colors.red,
                          () => Navigator.push(context, MaterialPageRoute(builder: (_) => EliminarUsuarioScreen())),
                        ),
                        _buildMenuCard(
                          context,
                          'Comparar Rostro',
                          Icons.camera_alt,
                          Colors.teal,
                          () => Navigator.push(context, MaterialPageRoute(builder: (_) => CompararRostroScreen())),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuCard(BuildContext context, String title, IconData icon, Color color, VoidCallback onTap) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                color.withOpacity(0.1),
                color.withOpacity(0.05),
              ],
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Icon(
                    icon,
                    size: 32,
                    color: color,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                    color: color,
                  ),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// Pantalla para registrar usuario (funcional)
class RegistrarUsuarioScreen extends StatefulWidget {
  @override
  _RegistrarUsuarioScreenState createState() => _RegistrarUsuarioScreenState();
}

class _RegistrarUsuarioScreenState extends State<RegistrarUsuarioScreen> {
  final _formKey = GlobalKey<FormState>();
  String nombre = '';
  String apellido = '';
  String codigo = '';
  String correo = '';
  bool requisitoriado = false;
  File? imagen;

  Future<void> pickImageCamera() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);
    if (pickedFile != null) {
      setState(() {
        imagen = File(pickedFile.path);
      });
    }
  }

  Future<void> pickImageGallery() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        imagen = File(pickedFile.path);
      });
    }
  }

  Future<void> registrarUsuario() async {
    print('Intentando registrar usuario...');
    if (imagen == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Selecciona una imagen')),
      );
      return;
    }
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('https://percepcion1314-production.up.railway.app/registrar_usuario'),
      );
      request.fields['nombre'] = nombre;
      request.fields['apellido'] = apellido;
      request.fields['codigo'] = codigo;
      request.fields['correo'] = correo;
      request.fields['requisitoriado'] = requisitoriado.toString();
      request.files.add(await http.MultipartFile.fromPath('imagen', imagen!.path));
      var response = await request.send();
      print('Status code: ${response.statusCode}');
      print('Response: ${await response.stream.bytesToString()}');
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Usuario registrado correctamente')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${response.statusCode}')),
        );
      }
    } catch (e) {
      print('Error al registrar usuario: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de red: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Registrar Usuario'),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF6750A4), Color(0xFF9C27B0)],
            ),
          ),
        ),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFF8F9FA), Color(0xFFE8EAF6)],
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Form(
            key: _formKey,
            child: ListView(
              children: [
                // Header con icono
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 10,
                        offset: const Offset(0, 5),
                      ),
                    ],
                  ),
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.blue.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Icon(
                          Icons.person_add,
                          size: 40,
                          color: Colors.blue,
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Nuevo Usuario',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                
                // Formulario
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        _buildTextField(
                          label: 'Nombre',
                          icon: Icons.person,
                          onChanged: (val) => nombre = val,
                        ),
                        const SizedBox(height: 16),
                        _buildTextField(
                          label: 'Apellido',
                          icon: Icons.person_outline,
                          onChanged: (val) => apellido = val,
                        ),
                        const SizedBox(height: 16),
                        _buildTextField(
                          label: 'Código',
                          icon: Icons.badge,
                          onChanged: (val) => codigo = val,
                        ),
                        const SizedBox(height: 16),
                        _buildTextField(
                          label: 'Correo',
                          icon: Icons.email,
                          onChanged: (val) => correo = val,
                        ),
                        const SizedBox(height: 16),
                        Container(
                          decoration: BoxDecoration(
                            color: Colors.grey[100],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: SwitchListTile(
                            title: const Text('Requisitoriado'),
                            subtitle: const Text('Marcar si el usuario tiene requisitoria'),
                            value: requisitoriado,
                            onChanged: (val) => setState(() => requisitoriado = val),
                            activeColor: Colors.red,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                
                // Sección de imagen
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        const Text(
                          'Foto del Usuario',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        imagen == null
                            ? Container(
                                height: 200,
                                decoration: BoxDecoration(
                                  color: Colors.grey[100],
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(color: Colors.grey[300]!),
                                ),
                                child: const Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      Icons.camera_alt,
                                      size: 50,
                                      color: Colors.grey,
                                    ),
                                    SizedBox(height: 8),
                                    Text(
                                      'No hay imagen seleccionada',
                                      style: TextStyle(color: Colors.grey),
                                    ),
                                  ],
                                ),
                              )
                            : Container(
                                height: 200,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(16),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withOpacity(0.1),
                                      blurRadius: 10,
                                      offset: const Offset(0, 5),
                                    ),
                                  ],
                                ),
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(16),
                                  child: Image.file(imagen!, fit: BoxFit.cover),
                                ),
                              ),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: pickImageCamera,
                                icon: const Icon(Icons.camera_alt),
                                label: const Text('Cámara'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.green,
                                  foregroundColor: Colors.white,
                                ),
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: pickImageGallery,
                                icon: const Icon(Icons.photo_library),
                                label: const Text('Galería'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.blue,
                                  foregroundColor: Colors.white,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                
                // Botón de registro
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: registrarUsuario,
                    icon: const Icon(Icons.save),
                    label: const Text(
                      'Registrar Usuario',
                      style: TextStyle(fontSize: 16),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required String label,
    required IconData icon,
    required Function(String) onChanged,
  }) {
    return TextFormField(
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: Colors.blue),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: Colors.blue, width: 2),
        ),
        filled: true,
        fillColor: Colors.grey[50],
      ),
      onChanged: onChanged,
    );
  }
}

// Pantalla para listar usuarios (funcional)
class ListaUsuariosScreen extends StatefulWidget {
  @override
  _ListaUsuariosScreenState createState() => _ListaUsuariosScreenState();
}

class _ListaUsuariosScreenState extends State<ListaUsuariosScreen> {
  List usuarios = [];
  bool cargando = true;

  @override
  void initState() {
    super.initState();
    cargarUsuarios();
  }

  Future<void> cargarUsuarios() async {
    final url = 'https://percepcion1314-production.up.railway.app/usuarios';
    final resp = await http.get(Uri.parse(url));
    if (resp.statusCode == 200) {
      setState(() {
        usuarios = json.decode(resp.body);
        cargando = false;
      });
    } else {
      setState(() {
        cargando = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cargar usuarios')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lista de Usuarios'),
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF6750A4), Color(0xFF9C27B0)],
            ),
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: cargarUsuarios,
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFFF8F9FA), Color(0xFFE8EAF6)],
          ),
        ),
        child: cargando
            ? const Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('Cargando usuarios...'),
                  ],
                ),
              )
            : usuarios.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(20),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.1),
                                blurRadius: 10,
                                offset: const Offset(0, 5),
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.people_outline,
                            size: 80,
                            color: Colors.grey,
                          ),
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          'No hay usuarios registrados',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Registra el primer usuario para comenzar',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: usuarios.length,
                    itemBuilder: (context, i) {
                      final u = usuarios[i];
                      final isRequisitoriado = u['requisitoriado'] == 1 || u['requisitoriado'] == true;
                      
                      return Card(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: Container(
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(16),
                            gradient: LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: isRequisitoriado
                                  ? [Colors.red[50]!, Colors.red[100]!]
                                  : [Colors.white, Colors.grey[50]!],
                            ),
                          ),
                          child: ListTile(
                            contentPadding: const EdgeInsets.all(16),
                            leading: CircleAvatar(
                              radius: 25,
                              backgroundColor: isRequisitoriado ? Colors.red : Colors.blue,
                              child: Icon(
                                Icons.person,
                                color: Colors.white,
                                size: 30,
                              ),
                            ),
                            title: Text(
                              '${u['nombre']} ${u['apellido']}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    const Icon(Icons.badge, size: 16, color: Colors.grey),
                                    const SizedBox(width: 4),
                                    Text('Código: ${u['codigo']}'),
                                  ],
                                ),
                                const SizedBox(height: 2),
                                Row(
                                  children: [
                                    const Icon(Icons.email, size: 16, color: Colors.grey),
                                    const SizedBox(width: 4),
                                    Expanded(
                                      child: Text(
                                        'Correo: ${u['correo']}',
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                            trailing: isRequisitoriado
                                ? Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: Colors.red,
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: const Row(
                                      mainAxisSize: MainAxisSize.min,
                                      children: [
                                        Icon(Icons.warning, color: Colors.white, size: 16),
                                        SizedBox(width: 4),
                                        Text(
                                          'ALERTA',
                                          style: TextStyle(
                                            color: Colors.white,
                                            fontSize: 10,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ],
                                    ),
                                  )
                                : Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: Colors.green,
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: const Text(
                                      'ACTIVO',
                                      style: TextStyle(
                                        color: Colors.white,
                                        fontSize: 10,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                          ),
                        ),
                      );
                    },
                  ),
      ),
    );
  }
}

// Pantalla para consultar usuario por código
class ConsultarUsuarioScreen extends StatefulWidget {
  @override
  _ConsultarUsuarioScreenState createState() => _ConsultarUsuarioScreenState();
}

class _ConsultarUsuarioScreenState extends State<ConsultarUsuarioScreen> {
  final _formKey = GlobalKey<FormState>();
  String codigo = '';
  Map<String, dynamic>? usuario;
  bool cargando = false;

  Future<void> consultarUsuario() async {
    if (codigo.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ingresa un código')),
      );
      return;
    }

    setState(() {
      cargando = true;
      usuario = null;
    });

    try {
      final url = 'https://percepcion1314-production.up.railway.app/usuario/$codigo';
      final resp = await http.get(Uri.parse(url));
      
      if (resp.statusCode == 200) {
        setState(() {
          usuario = json.decode(resp.body);
          cargando = false;
        });
      } else if (resp.statusCode == 404) {
        setState(() {
          usuario = null;
          cargando = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Usuario no encontrado')),
        );
      } else {
        setState(() {
          cargando = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al consultar usuario')),
        );
      }
    } catch (e) {
      setState(() {
        cargando = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de red: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Consultar Usuario por Código')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                decoration: InputDecoration(
                  labelText: 'Código del usuario',
                  border: OutlineInputBorder(),
                ),
                onChanged: (val) => codigo = val,
              ),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: cargando ? null : consultarUsuario,
                child: cargando 
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('Consultar Usuario'),
              ),
              SizedBox(height: 20),
              if (usuario != null) ...[
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${usuario!['nombre']} ${usuario!['apellido']}',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 8),
                        Text('Código: ${usuario!['codigo']}'),
                        Text('Correo: ${usuario!['correo']}'),
                        Text('Requisitoriado: ${usuario!['requisitoriado'] ? 'Sí' : 'No'}'),
                        if (usuario!['requisitoriado']) ...[
                          SizedBox(height: 8),
                          Container(
                            padding: EdgeInsets.all(8),
                            color: Colors.red[100],
                            child: Row(
                              children: [
                                Icon(Icons.warning, color: Colors.red),
                                SizedBox(width: 8),
                                Text('¡USUARIO REQUISITORIADO!', 
                                     style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// Pantalla para editar usuario existente
class EditarUsuarioScreen extends StatefulWidget {
  @override
  _EditarUsuarioScreenState createState() => _EditarUsuarioScreenState();
}

class _EditarUsuarioScreenState extends State<EditarUsuarioScreen> {
  final _formKey = GlobalKey<FormState>();
  String codigo = '';
  String nombre = '';
  String apellido = '';
  String correo = '';
  bool requisitoriado = false;
  File? imagen;
  bool cargando = false;
  Map<String, dynamic>? usuarioActual;

  Future<void> cargarUsuario() async {
    if (codigo.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ingresa un código')),
      );
      return;
    }

    setState(() {
      cargando = true;
    });

    try {
      final url = 'https://percepcion1314-production.up.railway.app/usuario/$codigo';
      final resp = await http.get(Uri.parse(url));
      
      if (resp.statusCode == 200) {
        final usuario = json.decode(resp.body);
        setState(() {
          usuarioActual = usuario;
          nombre = usuario['nombre'];
          apellido = usuario['apellido'];
          correo = usuario['correo'];
          requisitoriado = usuario['requisitoriado'];
          cargando = false;
        });
      } else {
        setState(() {
          cargando = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Usuario no encontrado')),
        );
      }
    } catch (e) {
      setState(() {
        cargando = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de red: $e')),
      );
    }
  }

  Future<void> pickImageCamera() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);
    if (pickedFile != null) {
      setState(() {
        imagen = File(pickedFile.path);
      });
    }
  }

  Future<void> pickImageGallery() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        imagen = File(pickedFile.path);
      });
    }
  }

  Future<void> actualizarUsuario() async {
    if (usuarioActual == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Primero carga un usuario')),
      );
      return;
    }

    setState(() {
      cargando = true;
    });

    try {
      var request = http.MultipartRequest(
        'PUT',
        Uri.parse('https://percepcion1314-production.up.railway.app/usuario/$codigo'),
      );
      
      request.fields['nombre'] = nombre;
      request.fields['apellido'] = apellido;
      request.fields['correo'] = correo;
      request.fields['requisitoriado'] = requisitoriado.toString();
      
      if (imagen != null) {
        request.files.add(await http.MultipartFile.fromPath('imagen', imagen!.path));
      }

      var response = await request.send();
      
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Usuario actualizado correctamente')),
        );
        // Recargar usuario actualizado
        cargarUsuario();
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${response.statusCode}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de red: $e')),
      );
    } finally {
      setState(() {
        cargando = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Editar Usuario Existente')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                decoration: InputDecoration(
                  labelText: 'Código del usuario',
                  border: OutlineInputBorder(),
                ),
                onChanged: (val) => codigo = val,
              ),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: cargando ? null : cargarUsuario,
                child: cargando 
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('Cargar Usuario'),
              ),
              if (usuarioActual != null) ...[
                SizedBox(height: 20),
                Text(
                  'Editando: ${usuarioActual!['nombre']} ${usuarioActual!['apellido']}',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 16),
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Nombre',
                    border: OutlineInputBorder(),
                  ),
                  initialValue: nombre,
                  onChanged: (val) => nombre = val,
                ),
                SizedBox(height: 16),
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Apellido',
                    border: OutlineInputBorder(),
                  ),
                  initialValue: apellido,
                  onChanged: (val) => apellido = val,
                ),
                SizedBox(height: 16),
                TextFormField(
                  decoration: InputDecoration(
                    labelText: 'Correo',
                    border: OutlineInputBorder(),
                  ),
                  initialValue: correo,
                  onChanged: (val) => correo = val,
                ),
                SizedBox(height: 16),
                SwitchListTile(
                  title: Text('Requisitoriado'),
                  value: requisitoriado,
                  onChanged: (val) => setState(() => requisitoriado = val),
                ),
                SizedBox(height: 16),
                Text('Nueva imagen (opcional):'),
                SizedBox(height: 10),
                imagen == null
                    ? Text('No hay imagen seleccionada')
                    : Image.file(imagen!, height: 150),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    ElevatedButton(
                      onPressed: pickImageCamera,
                      child: Text('Tomar Foto'),
                    ),
                    ElevatedButton(
                      onPressed: pickImageGallery,
                      child: Text('Subir Foto'),
                    ),
                  ],
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: cargando ? null : actualizarUsuario,
                  child: cargando 
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text('Actualizar Usuario'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// Pantalla para eliminar usuario por código
class EliminarUsuarioScreen extends StatefulWidget {
  @override
  _EliminarUsuarioScreenState createState() => _EliminarUsuarioScreenState();
}

class _EliminarUsuarioScreenState extends State<EliminarUsuarioScreen> {
  final _formKey = GlobalKey<FormState>();
  String codigo = '';
  bool cargando = false;
  Map<String, dynamic>? usuario;

  Future<void> cargarUsuario() async {
    if (codigo.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Ingresa un código')),
      );
      return;
    }

    setState(() {
      cargando = true;
      usuario = null;
    });

    try {
      final url = 'https://percepcion1314-production.up.railway.app/usuario/$codigo';
      final resp = await http.get(Uri.parse(url));
      
      if (resp.statusCode == 200) {
        setState(() {
          usuario = json.decode(resp.body);
          cargando = false;
        });
      } else {
        setState(() {
          cargando = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Usuario no encontrado')),
        );
      }
    } catch (e) {
      setState(() {
        cargando = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de red: $e')),
      );
    }
  }

  Future<void> eliminarUsuario() async {
    if (usuario == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Primero carga un usuario')),
      );
      return;
    }

    // Mostrar diálogo de confirmación
    bool confirmar = await showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('Confirmar eliminación'),
          content: Text('¿Estás seguro de que quieres eliminar a ${usuario!['nombre']} ${usuario!['apellido']}?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: Text('Cancelar'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              child: Text('Eliminar', style: TextStyle(color: Colors.red)),
            ),
          ],
        );
      },
    ) ?? false;

    if (!confirmar) return;

    setState(() {
      cargando = true;
    });

    try {
      final url = 'https://percepcion1314-production.up.railway.app/usuario/$codigo';
      final resp = await http.delete(Uri.parse(url));
      
      if (resp.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Usuario eliminado correctamente')),
        );
        setState(() {
          usuario = null;
          codigo = '';
        });
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al eliminar usuario')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de red: $e')),
      );
    } finally {
      setState(() {
        cargando = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Eliminar Usuario por Código')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                decoration: InputDecoration(
                  labelText: 'Código del usuario',
                  border: OutlineInputBorder(),
                ),
                onChanged: (val) => codigo = val,
              ),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: cargando ? null : cargarUsuario,
                child: cargando 
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('Cargar Usuario'),
              ),
              if (usuario != null) ...[
                SizedBox(height: 20),
                Card(
                  color: Colors.red[50],
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Usuario a eliminar:',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 8),
                        Text('${usuario!['nombre']} ${usuario!['apellido']}'),
                        Text('Código: ${usuario!['codigo']}'),
                        Text('Correo: ${usuario!['correo']}'),
                        SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: cargando ? null : eliminarUsuario,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            foregroundColor: Colors.white,
                          ),
                          child: cargando 
                            ? CircularProgressIndicator(color: Colors.white)
                            : Text('ELIMINAR USUARIO'),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// Pantalla para comparar rostro capturado
class CompararRostroScreen extends StatefulWidget {
  @override
  _CompararRostroScreenState createState() => _CompararRostroScreenState();
}

class _CompararRostroScreenState extends State<CompararRostroScreen> {
  File? imagen;
  bool cargando = false;
  Map<String, dynamic>? resultado;

  Future<void> pickImageCamera() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);
    if (pickedFile != null) {
      setState(() {
        imagen = File(pickedFile.path);
        resultado = null;
      });
    }
  }

  Future<void> pickImageGallery() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        imagen = File(pickedFile.path);
        resultado = null;
      });
    }
  }

  Future<void> compararRostro() async {
    if (imagen == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Selecciona una imagen')),
      );
      return;
    }

    setState(() {
      cargando = true;
      resultado = null;
    });

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('https://percepcion1314-production.up.railway.app/comparar_rostro'),
      );
      
      request.files.add(await http.MultipartFile.fromPath('imagen', imagen!.path));
      
      var response = await request.send();
      final responseBody = await response.stream.bytesToString();
      
      if (response.statusCode == 200) {
        setState(() {
          resultado = json.decode(responseBody);
          cargando = false;
        });
      } else {
        setState(() {
          cargando = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${response.statusCode}')),
        );
      }
    } catch (e) {
      setState(() {
        cargando = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error de red: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Comparar Rostro Capturado')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: ListView(
          children: [
            Text(
              'Captura o selecciona una imagen para comparar con la base de datos:',
              style: TextStyle(fontSize: 16),
            ),
            SizedBox(height: 20),
            imagen == null
                ? Container(
                    height: 200,
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.grey),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Text('No hay imagen seleccionada'),
                    ),
                  )
                : Image.file(imagen!, height: 200),
            SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: pickImageCamera,
                  child: Text('Tomar Foto'),
                ),
                ElevatedButton(
                  onPressed: pickImageGallery,
                  child: Text('Subir Foto'),
                ),
              ],
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: (imagen == null || cargando) ? null : compararRostro,
              child: cargando 
                ? CircularProgressIndicator(color: Colors.white)
                : Text('Comparar Rostro'),
            ),
            if (resultado != null) ...[
              SizedBox(height: 20),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        resultado!['mensaje'],
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      if (resultado!['usuario'] != null) ...[
                        SizedBox(height: 16),
                        Text('Usuario identificado:'),
                        Text('Nombre: ${resultado!['usuario']['nombre']} ${resultado!['usuario']['apellido']}'),
                        Text('Código: ${resultado!['usuario']['codigo']}'),
                        Text('Correo: ${resultado!['usuario']['correo']}'),
                        Text('Similitud: ${(resultado!['similitud'] * 100).toStringAsFixed(2)}%'),
                        if (resultado!['alerta'] == true) ...[
                          SizedBox(height: 16),
                          Container(
                            padding: EdgeInsets.all(12),
                            color: Colors.red[100],
                            child: Row(
                              children: [
                                Icon(Icons.warning, color: Colors.red),
                                SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    '🚨 ¡ALERTA DE SEGURIDAD! Usuario requisitoriado detectado.',
                                    style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ] else ...[
                        SizedBox(height: 16),
                        Text('Similitud máxima: ${(resultado!['similitud_maxima'] * 100).toStringAsFixed(2)}%'),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
