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
      title: 'Reconocimiento Facial',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: LandingPage(),
    );
  }
}

class LandingPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Menú Principal')),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          ElevatedButton(
            child: Text('Registrar nuevo usuario'),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => RegistrarUsuarioScreen())),
          ),
          ElevatedButton(
            child: Text('Lista de los usuarios'),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ListaUsuariosScreen())),
          ),
          ElevatedButton(
            child: Text('Consultar usuario por código'),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ConsultarUsuarioScreen())),
          ),
          ElevatedButton(
            child: Text('Editar usuario existente'),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => EditarUsuarioScreen())),
          ),
          ElevatedButton(
            child: Text('Eliminar usuario por código'),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => EliminarUsuarioScreen())),
          ),
          ElevatedButton(
            child: Text('Comparar rostro capturado'),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => CompararRostroScreen())),
          ),
        ],
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
      appBar: AppBar(title: Text('Registrar Usuario')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                decoration: InputDecoration(labelText: 'Nombre'),
                onChanged: (val) => nombre = val,
              ),
              TextFormField(
                decoration: InputDecoration(labelText: 'Apellido'),
                onChanged: (val) => apellido = val,
              ),
              TextFormField(
                decoration: InputDecoration(labelText: 'Código'),
                onChanged: (val) => codigo = val,
              ),
              TextFormField(
                decoration: InputDecoration(labelText: 'Correo'),
                onChanged: (val) => correo = val,
              ),
              SwitchListTile(
                title: Text('Requisitoriado'),
                value: requisitoriado,
                onChanged: (val) => setState(() => requisitoriado = val),
              ),
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
                onPressed: registrarUsuario,
                child: Text('Registrar Usuario'),
              ),
            ],
          ),
        ),
      ),
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
      appBar: AppBar(title: Text('Lista de Usuarios')),
      body: cargando
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: usuarios.length,
              itemBuilder: (context, i) {
                final u = usuarios[i];
                return ListTile(
                  title: Text('${u['nombre']} ${u['apellido']}'),
                  subtitle: Text('Código: ${u['codigo']} | Correo: ${u['correo']}'),
                  trailing: u['requisitoriado'] == 1 || u['requisitoriado'] == true
                      ? Icon(Icons.warning, color: Colors.red)
                      : null,
                );
              },
            ),
    );
  }
}

// Pantallas vacías para completar luego
class ConsultarUsuarioScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Consultar Usuario por Código')),
      body: Center(child: Text('Funcionalidad pendiente')), // Completar
    );
  }
}

class EditarUsuarioScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Editar Usuario Existente')),
      body: Center(child: Text('Funcionalidad pendiente')), // Completar
    );
  }
}

class EliminarUsuarioScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Eliminar Usuario por Código')),
      body: Center(child: Text('Funcionalidad pendiente')), // Completar
    );
  }
}

class CompararRostroScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Comparar Rostro Capturado')),
      body: Center(child: Text('Funcionalidad pendiente')), // Completar
    );
  }
}
