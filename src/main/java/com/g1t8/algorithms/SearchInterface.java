package com.g1t8.algorithms;

import java.util.List;

/**
 * Interface for all search implementations. All data structures must implement
 * this interface.
 */
public interface SearchInterface {

    /**
     * Builds the index/data structure from the list of reviews.
     *
     * @param reviews List of review texts to index
     */
    void buildIndex(List<String> reviews);

    /**
     * Searches for the given keyword.
     *
     * @param keyword The keyword to search for
     * @return List of review indices (0-based) containing the keyword
     */
    List<Integer> search(String keyword);

    /**
     * Gets the preprocessing time in milliseconds.
     *
     * @return Preprocessing time in ms
     */
    long getPreprocessingTime();

    /**
     * Gets the memory usage in bytes.
     *
     * @return Memory used in bytes
     */
    long getMemoryUsage();

    /**
     * Gets the name of the data structure.
     *
     * @return Structure name
     */
    String getStructureName();
}
