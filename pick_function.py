    def pick_champions_for_battlegrounds(self, count: int, champion_names: str) -> str:
        """Pick the best N champions for battlegrounds based on battlegrounds rating and ranking"""
        # Split the champion names by commas
        names = [name.strip() for name in champion_names.split(',')]
        
        champions = []
        
        # Find each champion
        for name in names:
            found_champs = self.data_manager.get_champion_by_name(name)
            if found_champs:
                # If multiple matches are found, use the first one
                champions.append(found_champs[0])
            # Note: We intentionally skip champions not found rather than creating defaults
        
        # Calculate battlegrounds-focused scores for each champion
        champion_scores = []
        for champion in champions:
            # Focus on battlegrounds rating as the primary factor
            if champion.rating is not None:
                # Champions with battlegrounds ratings get priority
                bg_score = champion.rating
                
                # Boost Dual Threat champions by 1 point as requested
                if champion.battlegrounds_type == "Dual Threat":
                    bg_score += 1
                
                # Add a small bonus based on ranking for tie-breaking
                ranking_bonus = 0
                if champion.category and '#' in champion.category:
                    try:
                        # Extract the ranking number after the '#'
                        ranking_part = champion.category.split('#')[1]
                        # Only take the first part if there are additional words after the number
                        ranking_num_str = ranking_part.split()[0] 
                        ranking_num = int(ranking_num_str)
                        # Higher ranked champions get a small bonus (1st gets more than 10th, etc.)
                        ranking_bonus = max(0, (50 - ranking_num) / 10)  # Scale down the bonus
                    except (IndexError, ValueError):
                        # If we can't parse the ranking, no bonus
                        ranking_bonus = 0
                
                # Total score prioritizes battlegrounds rating first, then ranking
                total_score = bg_score + ranking_bonus
                champion_scores.append((champion, total_score, True))  # True = has BG rating
            else:
                # Champions without battlegrounds ratings get a low base score
                # For these, we'll use ranking as the primary factor with a penalty
                ranking_score = 0
                if champion.category and '#' in champion.category:
                    try:
                        # Extract the ranking number after the '#'
                        ranking_part = champion.category.split('#')[1]
                        # Only take the first part if there are additional words after the number
                        ranking_num_str = ranking_part.split()[0] 
                        ranking_num = int(ranking_num_str)
                        # Higher ranked champions get higher scores (1st = 50, 10th = 40, etc.)
                        ranking_score = max(1, 50 - ranking_num)
                    except (IndexError, ValueError):
                        # If we can't parse the ranking, give a minimal score
                        ranking_score = 1
                
                # Apply a significant penalty for not having a battlegrounds rating
                total_score = ranking_score / 10  # Much lower than champions with ratings
                champion_scores.append((champion, total_score, False))  # False = no BG rating
        
        # Sort by total score descending, but prioritize champions with battlegrounds ratings
        # Primary sort: has battlegrounds rating (True > False)
        # Secondary sort: total score descending
        champion_scores.sort(key=lambda x: (x[2], x[1]), reverse=True)
        
        # Select the top N champions
        selected_champions = champion_scores[:count] if count > 0 else champion_scores
        
        # Format the results
        if not selected_champions:
            return "No champions found to pick from."
        
        response = f"**Top {count} Champions for Battlegrounds:**\n\n"
        
        for i, (champion, score, has_bg_rating) in enumerate(selected_champions, 1):
            rating_str = f"{champion.rating}/10" if champion.rating else "No BG rating"
            type_str = f" ({champion.battlegrounds_type})" if champion.battlegrounds_type else ""
            ranking_str = f" - {champion.category}" if champion.category else ""
            
            response += f"{i}. **{champion.name}**\n"
            response += f"   - Battlegrounds: {rating_str}{type_str}{ranking_str}\n"
            response += f"   - Tier: {champion.tier}\n\n"
        
        return response