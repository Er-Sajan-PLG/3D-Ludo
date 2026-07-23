using System.Collections.Generic;
using UnityEngine;

public enum GameState
{
    Lobby,
    Setup,
    Playing,
    Paused,
    Finished
}

[System.Serializable]
public class PlayerData
{
    public int playerId;
    public string playerName;
    public string color;
    public bool isActive = true;
    public bool isTurn = false;
    public List<int> currentPieces = new List<int>();
    public int lastRoll;
}

[System.Serializable]
public class PieceData
{
    public int pieceId;
    public int playerId;
    public int position;
    public bool isSelected;
    public bool reachedEnd;
}

public class GameManager : MonoBehaviour
{
    public GameState State = GameState.Setup;
    public int CurrentTurn = 0;
    public int CurrentPlayerIndex = 0;
    public List<PlayerData> Players = new List<PlayerData>();
    public List<PieceData> Pieces = new List<PieceData>();
    public int LastRoll = 0;

    private void Start()
    {
        InitializeGame(4, 4);
    }

    public void InitializeGame(int numPlayers, int piecesPerPlayer)
    {
        State = GameState.Playing;
        CurrentTurn = 1;
        Players.Clear();
        Pieces.Clear();

        for (int i = 0; i < numPlayers; i++)
        {
            var player = new PlayerData
            {
                playerId = i,
                playerName = $"Player {i + 1}",
                color = GetPlayerColor(i),
                isTurn = i == 0
            };

            for (int j = 0; j < piecesPerPlayer; j++)
            {
                int pieceId = i * 10 + j;
                player.currentPieces.Add(pieceId);

                Pieces.Add(new PieceData
                {
                    pieceId = pieceId,
                    playerId = i,
                    position = GetStartPosition(i),
                    isSelected = false,
                    reachedEnd = false
                });
            }

            Players.Add(player);
        }

        CurrentPlayerIndex = 0;
        LastRoll = 0;
    }

    private string GetPlayerColor(int index)
    {
        string[] colors = { "Red", "Blue", "Green", "Yellow" };
        return colors[index % colors.Length];
    }

    private int GetStartPosition(int playerId)
    {
        int[] startPositions = { 0, 13, 26, 39 };
        return startPositions[playerId % startPositions.Length];
    }

    public void PlayTurn()
    {
        if (State != GameState.Playing)
            return;

        var currentPlayer = Players[CurrentPlayerIndex];
        LastRoll = Random.Range(1, 7);
        MovePiece(currentPlayer, LastRoll);

        if (CheckWinCondition(currentPlayer))
        {
            State = GameState.Finished;
            Debug.Log($"Winner: {currentPlayer.playerName}");
            return;
        }

        NextTurn();
    }

    private void MovePiece(PlayerData player, int roll)
    {
        if (player.currentPieces.Count == 0)
            return;

        int pieceId = player.currentPieces[0];
        var piece = Pieces.Find(p => p.pieceId == pieceId);
        if (piece == null)
            return;

        piece.position += roll;
        piece.position = Mathf.Min(piece.position, 60);

        if (piece.position >= 60)
        {
            piece.reachedEnd = true;
        }
    }

    private void NextTurn()
    {
        Players[CurrentPlayerIndex].isTurn = false;
        CurrentPlayerIndex = (CurrentPlayerIndex + 1) % Players.Count;
        Players[CurrentPlayerIndex].isTurn = true;
        CurrentTurn += 1;
    }

    private bool CheckWinCondition(PlayerData player)
    {
        foreach (int id in player.currentPieces)
        {
            var piece = Pieces.Find(p => p.pieceId == id);
            if (piece == null || !piece.reachedEnd)
                return false;
        }
        return true;
    }
}
