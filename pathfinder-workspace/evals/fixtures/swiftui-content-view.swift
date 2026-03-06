import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            HomeView()
                .tabItem { Label("Home", systemImage: "house") }
            SettingsView()
                .tabItem { Label("Settings", systemImage: "gear") }
        }
    }
}

struct HomeView: View {
    var body: some View {
        NavigationStack {
            List {
                NavigationLink("Profile", destination: ProfileView())
                NavigationLink("Activity", destination: ActivityView())
            }
            .navigationTitle("Home")
        }
    }
}
