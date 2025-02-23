You are a senior developer responsible for a small team project. Provide an impartial analysis of the codebase’s progress for meeting our needs and outline the remaining tasks before it is ready for users. Both technical and business (non-technical) stakeholders will attend.

The project is a website that must:
1. Extract and present a view of a GraphQL response covering numerous items, including item-specific properties and multiple buy/sell options.
2. Store the GraphQL response in a Neo4j database efficiently, ensuring future data analysis capabilities.
3. Allow users to identify 1–5 items with a base value above 400000 while seeking the smallest “buyFor” value.
4. Offer manual item selection with word completion or automated optimal selection based on current pricing details.
5. Enable locking items in the selection, blacklisting items (temp or perm), and overriding prices—with an option to update the Neo4j database.
6. Provide a separate page for filtering and sorting items based on their different properties.
7. Adapt to a broad range of property types and handle variations in properties closely or exactly in structure. This view must extend beyond a simple table.
8. Let users quickly identify high-value items.
9. Use size, weight, stackability, and buy/sell prices for comparative analysis.
10. Offer review of item price histories from accumulated Neo4j data to identify profitable opportunities for crafting, bartering, purchasing, or finding items.
11. Run on two Docker containers (one Neo4j, one for all other tasks) with host GPU access.
12. Weigh the benefits of custom code against using existing packages.
13. Implement Material UI for the front end.
14. Use Material UI’s built-in dark/light themes rather than custom styling.
15. Avoid using Redis.
16. Follow best practices for an MVC project.
17. Deliver robust documentation for end users.
18. Maintain a record of business requirements from stakeholders and technical solution decisions for transparent change approvals. The site will run on local machines with separate databases, so the API connection is not always required, but containers must work together.