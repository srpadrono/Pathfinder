# Flutter Integration Tests

## Setup
```yaml
# pubspec.yaml
dev_dependencies:
  integration_test:
    sdk: flutter
  flutter_test:
    sdk: flutter
```

## Selectors
```dart
// Preferred
find.byKey(const Key('login-button'))
find.text('Submit')
find.byType(ElevatedButton)
find.bySemanticsLabel('Action button')

// Avoid
find.byElementPredicate(...)  // brittle
```

## Waits
```dart
await tester.pumpAndSettle()                    // wait for animations
await tester.pumpAndSettle(Duration(seconds: 5)) // with timeout
// NEVER: await Future.delayed(Duration(seconds: 3))
```

## Test Pattern
```dart
// integration_test/<checkpoint_id>_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('<CHECKPOINT_ID>: <description>', (tester) async {
    // Arrange
    app.main();
    await tester.pumpAndSettle();

    // Act
    await tester.tap(find.byKey(const Key('action-button')));
    await tester.pumpAndSettle();

    // Assert
    expect(find.text('Result'), findsOneWidget);
  });
}
```

## Screenshots
```dart
final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
await binding.takeScreenshot('<checkpoint-id>.png');
```

## Common Commands
| Action | Command |
|--------|---------|
| Run all | `flutter test integration_test/` |
| Run one | `flutter test integration_test/<checkpoint_id>_test.dart` |
| On device | `flutter test integration_test/ -d <device_id>` |
