import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Reconocimiento Facial',
      home: RegistroUsuarioScreen(),
    );
  }
}

class RegistroUsuarioScreen extends StatefulWidget {
  @override
  _RegistroUsuarioScreenState createState() => _RegistroUsuarioScreenState();
}

class _RegistroUsuarioScreenState extends State<RegistroUsuarioScreen> {
  final _formKey = GlobalKey<FormState>();
  String nombre = '';
  String apellido = '';
  String codigo = '';
  String correo = '';
  bool requisitoriado = false;
  File? imagen;

  Future<void> pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.camera);
    if (pickedFile != null) {
      setState(() {
        imagen = File(pickedFile.path);
      });
    }
  }

  Future<void> registrarUsuario() async {
    if (imagen == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Selecciona una imagen')),
      );
      return;
    }
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('https://a7f5-2800-200-fdc0-3874-145f-11f6-ed8e-68cb.ngrok-free.app/registrar_usuario'),
    );
    request.fields['nombre'] = nombre;
    request.fields['apellido'] = apellido;
    request.fields['codigo'] = codigo;
    request.fields['correo'] = correo;
    request.fields['requisitoriado'] = requisitoriado.toString();
    request.files.add(await http.MultipartFile.fromPath('imagen', imagen!.path));
    var response = await request.send();
    if (response.statusCode == 200) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Usuario registrado correctamente')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${response.statusCode}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Registro de Usuario')),
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
              ElevatedButton(
                onPressed: pickImage,
                child: Text('Tomar Foto'),
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
