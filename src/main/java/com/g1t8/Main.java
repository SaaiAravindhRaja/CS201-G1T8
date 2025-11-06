package com.g1t8;

import com.g1t8.algorithms.SearchInterface;
import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

/**
 * Main application for Skytrax Review Search System. Provides a console menu
 * for interacting with different search data structures.
 */
public class Main {

    private static final String CSV_FILE_PATH = "Skytrax User Reviews Dataset/airline.csv";
    private static Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        System.out.println("=========================");
        System.out.println();
        System.out.println("   SKYTRAX REVIEW SEARCH");
        System.out.println();
        System.out.println("=========================");
        System.out.println();

        // Load reviews (placeholder for now)
        List<String> reviews = loadReviews();

        if (reviews.isEmpty()) {
            System.out.println("Error: No reviews loaded. Please check the CSV file path.");
            return;
        }

        System.out.println("Loaded " + reviews.size() + " reviews.");
        System.out.println();

        // Main menu loop
        boolean running = true;
        while (running) {
            int choice = showMainMenu();

            if (choice == 0) {
                running = false;
                System.out.println("Thank you for using Skytrax Review Search!");
            } else {
                handleSearchChoice(choice, reviews);
            }
        }

        scanner.close();
    }

    /**
     * Displays the main menu and returns user's choice.
     */
    private static int showMainMenu() {
        System.out.println("Choose a data structure:");
        System.out.println();
        System.out.println("1. ArrayList (Linear Scan)");
        System.out.println("2. Inverted Index (HashMap)");
        System.out.println("3. Trie (Prefix Search)");
        System.out.println("4. Suffix Array");
        System.out.println("5. Bloom Filter");
        System.out.println("0. Exit");
        System.out.println();
        System.out.print("Enter choice [0-5]: ");

        try {
            int choice = Integer.parseInt(scanner.nextLine().trim());
            if (choice >= 0 && choice <= 5) {
                return choice;
            } else {
                System.out.println("Invalid choice. Please enter a number between 0 and 5.");
                System.out.println();
                return showMainMenu();
            }
        } catch (NumberFormatException e) {
            System.out.println("Invalid input. Please enter a number.");
            System.out.println();
            return showMainMenu();
        }
    }

    /**
     * Handles the user's search choice.
     */
    private static void handleSearchChoice(int choice, List<String> reviews) {
        System.out.println();

        // Get the appropriate search implementation
        // TODO: Replace with actual implementations
        SearchInterface searchImpl = getSearchImplementation(choice);

        if (searchImpl == null) {
            System.out.println("This data structure is not yet implemented.");
            System.out.println();
            return;
        }

        // Build index
        System.out.println("Building index using " + searchImpl.getStructureName() + "...");
        System.out.println();

        long startTime = System.currentTimeMillis();
        searchImpl.buildIndex(reviews);
        long preprocessingTime = System.currentTimeMillis() - startTime;

        // Calculate memory usage (simplified)
        Runtime runtime = Runtime.getRuntime();
        long memoryBefore = runtime.totalMemory() - runtime.freeMemory();
        System.gc(); // Suggest garbage collection
        long memoryAfter = runtime.totalMemory() - runtime.freeMemory();
        long memoryUsed = Math.max(0, memoryAfter - memoryBefore);

        System.out.println("Preprocessing complete in "
                + String.format("%.2f", preprocessingTime / 1000.0) + " seconds.");
        System.out.println("Memory used: "
                + String.format("%.2f", memoryUsed / (1024.0 * 1024.0)) + " MB.");
        System.out.println();
        System.out.println("---------------------------------------");
        System.out.println();

        // Search loop
        boolean searchAgain = true;
        while (searchAgain) {
            System.out.print("Enter keyword to search: ");
            String keyword = scanner.nextLine().trim();

            if (keyword.isEmpty()) {
                System.out.println("Keyword cannot be empty. Please try again.");
                continue;
            }

            System.out.println();
            System.out.println("---------------------------------------");
            System.out.println();
            System.out.println("Searching for keyword \"" + keyword + "\"...");

            long searchStartTime = System.nanoTime();
            List<Integer> results = searchImpl.search(keyword);
            long searchTime = (System.nanoTime() - searchStartTime) / 1_000_000; // Convert to ms

            System.out.println();
            System.out.println("Found in " + results.size() + " reviews.");
            System.out.println("Query time: "
                    + String.format("%.2f", searchTime / 1000.0) + " ms");
            System.out.println();

            // Display sample results
            if (results.size() > 0) {
                System.out.println("Sample results:");
                int sampleSize = Math.min(3, results.size());
                for (int i = 0; i < sampleSize; i++) {
                    int reviewIndex = results.get(i);
                    String reviewText = reviews.get(reviewIndex);
                    // Truncate if too long
                    if (reviewText.length() > 80) {
                        reviewText = reviewText.substring(0, 77) + "...";
                    }
                    System.out.println("[" + reviewIndex + "] \"" + reviewText + "\"");
                }
                if (results.size() > 3) {
                    System.out.println("... and " + (results.size() - 3) + " more results.");
                }
            } else {
                System.out.println("No reviews found containing \"" + keyword + "\".");
            }

            System.out.println();
            System.out.println("---------------------------------------");
            System.out.println();

            // Ask if user wants to search again
            System.out.print("Search again? (y/n): ");
            String response = scanner.nextLine().trim().toLowerCase();
            searchAgain = response.equals("y") || response.equals("yes");
            System.out.println();
        }
    }

    /**
     * Returns the appropriate search implementation based on user's choice.
     * TODO: Replace with actual implementations.
     */
    private static SearchInterface getSearchImplementation(int choice) {
        // TODO: Replace these with actual implementations
        switch (choice) {
            case 1:
                // return new ArrayListSearch();
                return new PlaceholderSearch("ArrayList (Linear Scan)");
            case 2:
                // return new InvertedIndexSearch();
                return new PlaceholderSearch("Inverted Index (HashMap)");
            case 3:
                // return new TrieSearch();
                return new PlaceholderSearch("Trie (Prefix Search)");
            case 4:
                // return new SuffixArraySearch();
                return new PlaceholderSearch("Suffix Array");
            case 5:
                // return new BloomFilterSearch();
                return new PlaceholderSearch("Bloom Filter");
            default:
                return null;
        }
    }

    /**
     * Loads reviews from CSV file. TODO: Implement actual CSV parsing.
     */
    private static List<String> loadReviews() {
        List<String> reviews = new ArrayList<>();

        // TODO: Implement CSV parsing
        return reviews;
    }

    /**
     * Placeholder search implementation for testing the menu. Remove this once
     * you implement actual search structures.
     */
    //No need to implement this
    private static class PlaceholderSearch implements SearchInterface {

        private String structureName;
        private long preprocessingTime = 0;

        public PlaceholderSearch(String structureName) {
            this.structureName = structureName;
        }

        @Override
        public void buildIndex(List<String> reviews) {
            // Simulate preprocessing
            try {
                Thread.sleep(100); // Simulate work
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            preprocessingTime = 100;
        }

        @Override
        public List<Integer> search(String keyword) {
            // Placeholder: return empty list for now
            return new ArrayList<>();
        }

        @Override
        public long getPreprocessingTime() {
            return preprocessingTime;
        }

        @Override
        public long getMemoryUsage() {
            return 82 * 1024 * 1024; // Simulate 82 MB
        }

        @Override
        public String getStructureName() {
            return structureName;
        }
    }
}
