import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Student Career Helper',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.redAccent),
      ),
      home: const MyHomePage(title: 'Student Career Helper'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});
  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  List<String> skillList = [];
  final TextEditingController _textEditingController = TextEditingController();

  @override
  void dispose() {
    _textEditingController.dispose();
    super.dispose();
  }

  Future<List<String>> _fetchSkillSuggestions(String query, int? limit) async {
    var response;
    if (limit != null)
      response = await http.get(
        Uri.parse(
          'http://localhost:6969/search-skill?keyword=$query&limit=$limit',
        ),
      );
    else
      response = await http.get(
        Uri.parse('http://localhost:6969/search-skill?keyword=$query'),
      );

    if (response.statusCode == 200) {
      List<String> suggestions = List<String>.from(jsonDecode(response.body));
      return suggestions;
    } else {
      throw Exception('Failed to load suggestions');
    }
  }

  Widget _buildTab1(BuildContext context) {
    return Row(
      children: [
        Expanded(
          flex: 1,
          child: Column(
            children: [
              Text("Choose skill"),
              SingleChildScrollView(
                child: Wrap(
                  children: skillList.map((item) {
                    return Chip(
                      label: Text(item),
                      deleteIcon: const Icon(Icons.close, size: 18),
                      onDeleted: () {
                        setState(() {
                          skillList.remove(item);
                        });
                      },
                    );
                  }).toList(),
                ),
              ),
              Autocomplete<String>(
                optionsBuilder: (TextEditingValue textEditingValue) {
                  if (textEditingValue.text.isEmpty) {
                    return const Iterable<String>.empty();
                  }

                  return _fetchSkillSuggestions(textEditingValue.text, null);
                },

                // Display the selected option in the text field
                fieldViewBuilder:
                    (
                      BuildContext context,
                      TextEditingController fieldTextEditingController,
                      FocusNode fieldFocusNode,
                      VoidCallback onFieldSubmitted,
                    ) {
                      // Use the internal controller to keep track of the text
                      fieldTextEditingController.text = _textEditingController.text;

                      return TextField(
                        controller: fieldTextEditingController,
                        focusNode: fieldFocusNode,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'Start typing...',
                        ),
                      );
                    },

                // Logic for when an item is selected from the dropdown
                onSelected: (String selection) {
                  // Check if the item is not already in the list
                  setState(() {
                    skillList.add(selection);
                    _textEditingController.clear();
                  });
                  // Clear the input field after selection
                },
              ),
            ],
          ),
        ),
        Expanded(
          flex: 1,
          child: Container(
            color: Colors.white,
            child: Center(child: Text('Detail View Area')),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: Text(widget.title),
          bottom: TabBar(
            tabs: [
              Tab(icon: Icon(Icons.favorite), text: 'Favorites'),
              Tab(icon: Icon(Icons.music_note), text: 'Music'),
              Tab(icon: Icon(Icons.movie), text: 'Movies'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildTab1(context),
            Center(child: Text('Music Tab Content')),
            Center(child: Text('Movies Tab Content')),
          ],
        ),
      ),
    );
  }
}
