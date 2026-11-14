import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:snapdiet/main.dart';

void main() {
  testWidgets('App loads smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const SnapDietApp());

    // Verify that our app bar title is present.
    expect(find.text('SnapDiet'), findsOneWidget);
  });
}
